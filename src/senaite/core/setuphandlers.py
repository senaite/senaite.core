# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims.setuphandlers import add_dexterity_setup_items
from bika.lims.setuphandlers import reindex_content_structure
from bika.lims.setuphandlers import setup_auditlog_catalog
from bika.lims.setuphandlers import setup_catalog_mappings
from bika.lims.setuphandlers import setup_core_catalogs
from bika.lims.setuphandlers import setup_form_controller_actions
from bika.lims.setuphandlers import setup_groups
from senaite.core import logger
from senaite.core.config import PROFILE_ID
from zope.interface import implementer

try:
    from Products.CMFPlone.interfaces import INonInstallable
except ImportError:
    from zope.interface import Interface

    class INonInstallable(Interface):
        pass


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide all profiles from site-creation and quickinstaller (not ZMI)"""
        return [
            # Leave visible to allow upgrade via the Plone Add-on controlpanel
            # "bika.lims:default",

            # hide install profiles that come with Plone
            "Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow",
            "Products.CMFPlacefulWorkflow:base",
            "Products.CMFPlacefulWorkflow:uninstall",
            "Products.DataGridField:default",
            "Products.DataGridField:example",
            "Products.TextIndexNG3:default",
            "archetypes.multilingual:default",
            "archetypes.referencebrowserwidget:default",
            "collective.js.jqueryui:default"
            "plone.app.iterate:default",
            "plone.app.iterate:plone.app.iterate",
            "plone.app.iterate:test",
            "plone.app.iterate:uninstall",
            "plone.app.jquery:default",
            "plonetheme.barceloneta:default",
        ]


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
    _run_import_step(portal, "typeinfo")
    _run_import_step(portal, "factorytool")
    _run_import_step(portal, "workflow")

    # Run Installers
    setup_groups(portal)
    remove_default_content(portal)
    setup_core_catalogs(portal)
    setup_content_structure(portal)
    add_dexterity_setup_items(portal)
    setup_catalog_mappings(portal)

    # Run after all catalogs have been setup
    setup_auditlog_catalog(portal)

    # Set CMF Form actions
    setup_form_controller_actions(portal)
    setup_form_controller_more_action(portal)

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


def setup_content_structure(portal):
    """Install the base content structure
    """
    logger.info("*** Install SENAITE Content Types ***")
    _run_import_step(portal, "content")
    reindex_content_structure(portal)


def setup_form_controller_more_action(portal):
    """Install form controller actions for ported record widgets

    Code taken from Products.ATExtensions
    """
    logger.info("*** Install SENAITE Form Controller Actions ***")
    pfc = portal.portal_form_controller
    pfc.addFormValidators(
        "base_edit", "", "more", "")
    pfc.addFormAction(
        "base_edit", "success", "", "more", "traverse_to", "string:more_edit")
    pfc.addFormValidators(
        "atct_edit", "", "more", "",)
    pfc.addFormAction(
        "atct_edit", "success", "", "more", "traverse_to", "string:more_edit")


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

    # always apply the skins profile last to ensure our layers are first
    _run_import_step(portal, "skins", profile=profile_id)

    logger.info("SENAITE CORE post install handler [DONE]")
