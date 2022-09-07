# -*- coding: utf-8 -*-

import transaction
from AccessControl.SecurityManagement import newSecurityManager
from bika.lims import api
from senaite.core import logger
from senaite.core.decorators import retriable
from senaite.core.scripts import parser
from senaite.core.scripts.utils import setup_site

__doc__ = """Run upgrade profiles on sites
"""

parser.description = __doc__


def get_site_ids(app):
    """Returns a list of available site ids
    """
    sites = app.objectValues("Plone Site")
    return map(api.get_id, sites)


def run_last_upgrade_step(portal_setup, profile_id):
    """Run the last upgrade step
    """
    upgrades = portal_setup.listUpgrades(profile_id, show_old=True)

    # we always take the last upgrade step
    if not upgrades:
        return

    upgrade = upgrades[-1]
    step = upgrade.get("step")
    if step:
        sdest = upgrade.get("sdest")
        logger.debug("Running upgrade step %s for profile %s"
                     % (sdest, profile_id))
        step.doStep(portal_setup)


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
        run_last_upgrade_step(ps, profile_id)
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
    run(app) # noqa: F821
