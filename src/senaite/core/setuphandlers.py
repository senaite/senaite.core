# -*- coding: utf-8 -*-

from bika.lims import api
from plone import api as ploneapi
from senaite.core import logger
from senaite.core.config import CONTENTS_TO_DELETE
from senaite.core.config import GROUPS
from senaite.core.config import PROFILE_ID


def install(context):
    """Install handler
    """
    if context.readDataFile("senaite.core.txt") is None:
        return

    logger.info("SENAITE CORE install handler [BEGIN]")
    portal = context.getSite()

    # Run Installers
    remove_default_content(portal)
    setup_groups(portal)
    install_contenttypes_and_structure(portal)

    logger.info("SENAITE CORE install handler [DONE]")


def remove_default_content(portal):
    """Remove default Plone contents
    """
    logger.info("*** Delete Default Content ***")

    # Get the list of object ids for portal
    object_ids = portal.objectIds()
    delete_ids = filter(lambda id: id in object_ids, CONTENTS_TO_DELETE)
    if len(delete_ids) > 0:
        portal.manage_delObjects(ids=list(delete_ids))


def setup_groups(portal):
    """Setup roles and groups
    """
    logger.info("*** Setup Roles and Groups ***")

    portal_groups = api.get_tool("portal_groups")

    for gdata in GROUPS:
        group_id = gdata["id"]
        # create the group and grant the roles
        if group_id not in portal_groups.listGroupIds():
            logger.info("+++ Adding group {title} ({id})".format(**gdata))
            portal_groups.addGroup(group_id,
                                   title=gdata["title"],
                                   roles=gdata["roles"])
        # grant the roles to the existing group
        else:
            ploneapi.group.grant_roles(
                groupname=gdata["id"],
                roles=gdata["roles"],)
            logger.info("+++ Granted group {title} ({id}) the roles {roles}"
                        .format(**gdata))


def install_contenttypes_and_structure(portal):
    """Install AT contenttypes
    """
    logger.info("*** Install Content Types and Structure ***")
    profile = "profile-bika.lims:default"
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "content")
    # setup.runImportStepFromProfile(profile, "structure")


def pre_install(portal_setup):
    """Runs berfore the first import step of the *default* profile

    This handler is registered as a *pre_handler* in the generic setup profile

    :param portal_setup: SetupTool
    """
    logger.info("SENAITE CORE pre-install handler [BEGIN]")

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = PROFILE_ID
    context = portal_setup._getImportContext(profile_id)
    portal = context.getSite()  # noqa

    # Only install the core once!
    # qi = portal.portal_quickinstaller
    # if not qi.isProductInstalled("bika.lims"):
    #     portal_setup.runAllImportStepsFromProfile("profile-bika.lims:default")

    logger.info("SENAITE CORE pre-install handler [DONE]")


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile

    This handler is registered as a *post_handler* in the generic setup profile

    :param portal_setup: SetupTool
    """
    logger.info("SENAITE CORE post install handler [BEGIN]")

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = PROFILE_ID
    context = portal_setup._getImportContext(profile_id)
    portal = context.getSite()  # noqa

    logger.info("SENAITE CORE post install handler [DONE]")
