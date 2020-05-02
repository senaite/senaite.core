# -*- coding: utf-8 -*-

from bika.lims.setuphandlers import add_dexterity_setup_items
from bika.lims.setuphandlers import reindex_content_structure
from bika.lims.setuphandlers import setup_auditlog_catalog
from bika.lims.setuphandlers import setup_catalog_mappings
from bika.lims.setuphandlers import setup_core_catalogs
from bika.lims.setuphandlers import setup_groups
from senaite.core import logger
from senaite.core.config import PROFILE_ID

CONTENTS_TO_DELETE = (
    # List of items to delete
    "Members",
    "news",
    "events",
)


def install(context):
    """Install handler
    """
    if context.readDataFile("senaite.core.txt") is None:
        return

    logger.info("SENAITE CORE install handler [BEGIN]")
    portal = context.getSite()

    # Run required import steps
    _run_import_step(portal, "skins")
    _run_import_step(portal, "browserlayer")
    _run_import_step(portal, "rolemap")
    _run_import_step(portal, "toolset")  # catalogs
    _run_import_step(portal, "workflow")

    # Run Installers
    setup_groups(portal)
    remove_default_content(portal)
    setup_content_types(portal)
    setup_core_catalogs(portal)
    setup_auditlog_catalog(portal)
    setup_content_structure(portal)
    add_dexterity_setup_items(portal)
    setup_catalog_mappings(portal)

    logger.info("SENAITE CORE install handler [DONE]")


def remove_default_content(portal):
    """Remove default Plone contents
    """
    logger.info("*** Remove Default Content ***")

    # Get the list of object ids for portal
    object_ids = portal.objectIds()
    delete_ids = filter(lambda id: id in object_ids, CONTENTS_TO_DELETE)
    if delete_ids:
        portal.manage_delObjects(ids=list(delete_ids))


def setup_content_types(portal):
    """Install AT content type information
    """
    logger.info("*** Install SENAITE Content Types ***")
    _run_import_step(portal, "typeinfo")
    _run_import_step(portal, "factorytool")


def setup_content_structure(portal):
    """Install the base content structure
    """
    logger.info("*** Install SENAITE Content Types ***")
    _run_import_step(portal, "content")
    reindex_content_structure(portal)


def _run_import_step(portal, name, profile="profile-bika.lims:default"):
    """Helper to install a GS import step from the given profile
    """
    logger.info("*** Running import step '{}' from profile '{}' ***"
                .format(name, profile))
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, name)


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
