# -*- coding: utf-8 -*-

import transaction
from AccessControl.SecurityManagement import newSecurityManager
from bika.lims import api
from senaite.core import logger
from senaite.core.decorators import retriable
from senaite.core.scripts import parser
from zope.component.hooks import setSite
from zope.event import notify
from zope.globalrequest import setRequest
from zope.traversing.interfaces import BeforeTraverseEvent

__doc__ = """Run upgrade profiles on sites
"""

parser.description = __doc__


def get_site_ids(app):
    """Returns a list of available site ids
    """
    sites = app.objectValues("Plone Site")
    return map(api.get_id, sites)


def setup_site(site):
    setSite(site)
    site.clearCurrentSkin()
    site.setupCurrentSkin(site.REQUEST)
    notify(BeforeTraverseEvent(site, site.REQUEST))
    setRequest(site.REQUEST)


def run_upgrades_until_stuck(portal_setup,
                             profile_id,
                             original_steps_to_run=None,
                             first_iteration=False):
    steps_to_run = portal_setup.listUpgrades(profile_id)
    if steps_to_run:
        if first_iteration:
            logger.debug("Running profile upgrades for {}".format(profile_id))
        elif steps_to_run == original_steps_to_run:
            return steps_to_run
        portal_setup.upgradeProfile(profile_id)
        return run_upgrades_until_stuck(
            portal_setup,
            profile_id,
            steps_to_run,
        )


@retriable(sync=True)
def upgrade(site):
    setup_site(site)

    # attempt to upgrade plone first
    pm = site.portal_migration
    report = pm.upgrade(dry_run=False)
    if report:
        logger.debug(report)
    ps = site.portal_setup
    # go through all profiles that need upgrading
    for profile_id in ps.listProfilesWithUpgrades():
        if not profile_id.startswith("senaite"):
            continue
        remaining = run_upgrades_until_stuck(
            ps, profile_id, first_iteration=True)
        if remaining:
            raise Exception(
                '[{}] Running upgrades did not finish all upgrade steps: {}'
                .format(profile_id, remaining))

    transaction.commit()


def run(app):
    args, _ = parser.parse_known_args()
    user = app.acl_users.getUser("admin")
    newSecurityManager(None, user.__of__(app.acl_users))

    if args.site_id:
        site = app[args.site_id]
        upgrade(site)
    else:
        for sid in get_site_ids(app):
            site = app[sid]
            upgrade(site)


if __name__ == "__main__":
    run(app)  # noqa
