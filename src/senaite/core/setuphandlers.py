# -*- coding: utf-8 -*-

from bika.lims.setuphandlers import reindex_content_structure
from bika.lims.setuphandlers import setup_catalog_mappings
from bika.lims.setuphandlers import setup_core_catalogs
from bika.lims.setuphandlers import setup_groups
from senaite.core import logger
from senaite.core.config import PROFILE_ID


def install(context):
    """Install handler
    """
    if context.readDataFile("senaite.core.txt") is None:
        return

    logger.info("SENAITE CORE install handler [BEGIN]")
    portal = context.getSite()

    # Run Installers
    setup_first(portal)
    setup_content_types(portal)
    setup_core_catalogs(portal)
    setup_content_structure(portal)
    setup_catalog_mappings(portal)

    logger.info("SENAITE CORE install handler [DONE]")


def setup_first(portal):
    """Various import steps that can be run first
    """
    setup_groups(portal)
    _run_import_step(portal, "skins")


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
