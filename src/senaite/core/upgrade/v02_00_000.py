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

from bika.lims import api
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.setuphandlers import add_dexterity_setup_items
from senaite.core import logger
from senaite.core.config import PROJECTNAME as product
from senaite.core.setuphandlers import _run_import_step
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils

version = "2.0.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

INSTALL_PRODUCTS = [
    "senaite.core",
]

UNINSTALL_PRODUCTS = [
    "collective.js.jqueryui",
    "plone.app.discussion",
    "plone.app.event",
    "plone.app.theming",
    "plone.portlet.collection",
    "plonetheme.barceloneta",
]


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------

    # Remove duplicate methods from analysis services
    remove_duplicate_methods_in_services(portal)

    # Uninstall default Plone 5 Addons
    uninstall_default_plone_addons(portal)

    # Install the new SENAITE CORE package
    install_senaite_core(portal)

    # run import steps located in senaite.core profiles
    setup.runImportStepFromProfile(profile, "typeinfo")
    setup.runImportStepFromProfile(profile, "workflow")
    # run import steps located in bika.lims profiles
    _run_import_step(portal, "typeinfo", profile="profile-bika.lims:default")
    _run_import_step(portal, "workflow", profile="profile-bika.lims:default")

    add_dexterity_setup_items(portal)

    # Published results tab is not displayed to client contacts
    # https://github.com/senaite/senaite.core/pull/1638
    fix_published_results_permission(portal)

    # Update workflow mappings for samples to allow profile editing
    update_workflow_mappings_samples(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_duplicate_methods_in_services(portal):
    """A bug caused duplicate methods stored in services which need to be fixed
    """
    logger.info("Remove duplicate methods from services...")

    cat = api.get_tool(SETUP_CATALOG)
    services = cat({"portal_type": "AnalysisService"})
    total = len(services)

    for num, service in enumerate(services):
        if num and num % 10 == 0:
            logger.info("Processed {}/{} Services".format(num, total))
        obj = api.get_object(service)
        methods = list(set(obj.getRawMethods()))
        if not methods:
            continue
        obj.setMethods(methods)
        obj.reindexObject()

    logger.info("Remove duplicate methods from services [DONE]")


def uninstall_default_plone_addons(portal):
    """Uninstall Plone Addons
    """
    logger.info("Uninstalling default Plone 5 Addons...")
    qi = api.get_tool("portal_quickinstaller")

    for p in UNINSTALL_PRODUCTS:
        if not qi.isProductInstalled(p):
            continue
        logger.info("Uninstalling '{}' ...".format(p))
        qi.uninstallProducts(products=[p])
    logger.info("Uninstalling default Plone 5 Addons [DONE]")


def install_senaite_core(portal):
    """Install new SENAITE CORE Add-on
    """
    logger.info("Installing SENAITE CORE 2.x...")
    qi = api.get_tool("portal_quickinstaller")

    for p in INSTALL_PRODUCTS:
        if qi.isProductInstalled(p):
            continue
        logger.info("Installing '{}' ...".format(p))
        qi.installProduct(p)
    logger.info("Installing SENAITE CORE 2.x [DONE]")


def fix_published_results_permission(portal):
    """Resets the permissions for action 'published_results' from
    AnalysisRequest portal type to 'View'
    """
    ti = portal.portal_types.getTypeInfo("AnalysisRequest")
    for action in ti.listActions():
        if action.id == "published_results":
            action.permissions = ("View", )
            break


def update_workflow_mappings_samples(portal):
    """Allow to edit analysis profiles
    """
    logger.info("Updating role mappings for Samples ...")
    wf_id = "bika_ar_workflow"
    query = {"portal_type": "AnalysisRequest",
             "review_state": [
                 "sample_due",
                 "sample_registered",
                 "scheduled_sampling",
                 "to_be_sampled",
                 "sample_received",
                 "attachment_due",
                 "to_be_verified",
                 "to_be_preserved",
             ]}
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    update_workflow_mappings_for(portal, wf_id, brains)
    logger.info("Updating role mappings for Samples [DONE]")


def update_workflow_mappings_for(portal, wf_id, brains):
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating role mappings: {0}/{1}".format(num, total))
        obj = api.get_object(brain)
        workflow.updateRoleMappingsFor(obj)
        obj.reindexObject(idxs=["allowedRolesAndUsers"])
