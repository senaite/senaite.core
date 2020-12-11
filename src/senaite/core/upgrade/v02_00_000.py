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

import time
import traceback

import transaction
from bika.lims import api
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.setuphandlers import add_dexterity_setup_items
from bika.lims.utils import changeWorkflowState
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

INDEXES_TO_ADD = [
    # List of tuples (catalog_name, index_name, index meta type)
    (SETUP_CATALOG, "department_id", "KeywordIndex"),
]

METADATA_TO_REMOVE = [
    # Only used in Analyses listing and it's behavior is bizarre, probably
    # because is a dict and requires special care with ZODB
    (CATALOG_ANALYSIS_LISTING, "getInterimFields"),
    # No longer used, see https://github.com/senaite/senaite.core/pull/1709/
    (CATALOG_ANALYSIS_LISTING, "getAttachmentUIDs")
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
    setup.runImportStepFromProfile(profile, "browserlayer")
    setup.runImportStepFromProfile(profile, "viewlets")
    # run import steps located in bika.lims profiles
    _run_import_step(portal, "typeinfo", profile="profile-bika.lims:default")
    _run_import_step(portal, "workflow", profile="profile-bika.lims:default")

    add_dexterity_setup_items(portal)

    # Published results tab is not displayed to client contacts
    # https://github.com/senaite/senaite.core/pull/1638
    fix_published_results_permission(portal)

    # Update workflow mappings for samples to allow profile editing
    update_workflow_mappings_samples(portal)

    # Initialize new department ID field
    # https://github.com/senaite/senaite.core/pull/1676
    initialize_department_id_field(portal)

    # Add new indexes
    add_new_indexes(portal)

    # Remove Supplyorders
    remove_supplyorder_action_from_clients(portal)
    remove_supplyorder_folder(portal)
    remove_all_supplyorders(portal)
    remove_supplyorder_typeinfo(portal)
    remove_supplyorder_workflow(portal)

    # Remove stale metadata
    remove_stale_metadata(portal)

    # Resolve objects in attachment_due
    resolve_attachment_due(portal)

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


def initialize_department_id_field(portal):
    """Initialize the new department ID field
    """
    logger.info("Initialize department ID field ...")
    query = {"portal_type": "Department"}
    brains = api.search(query, SETUP_CATALOG)
    objs = map(api.get_object, brains)
    department_ids = filter(None, map(lambda obj: obj.getDepartmentID(), objs))
    for obj in objs:
        department_id = obj.getDepartmentID()
        if department_id:
            continue
        # generate a sane department id
        title = api.get_title(obj)
        parts = title.split()
        idx = 1

        # Generate a new unique department ID with the first characters of the
        # department title.
        new_id = "".join(map(lambda p: p[0:idx], parts))
        while new_id in department_ids:
            idx += 1
            new_id = "".join(map(lambda p: p[0:idx], parts))
        try:
            # check if the new ID is avalid UTF8
            new_id = new_id.decode("utf8")
        except UnicodeDecodeError:
            # fallback to title
            new_id = title
        department_ids.append(new_id)
        obj.setDepartmentID(new_id)


def add_new_indexes(portal):
    logger.info("Adding new indexes ...")
    for catalog_id, index_name, index_metatype in INDEXES_TO_ADD:
        add_index(catalog_id, index_name, index_metatype)
    logger.info("Adding new indexes ... [DONE]")


def add_index(catalog_id, index_name, index_metatype):
    logger.info("Adding '{}' index to '{}' ...".format(index_name, catalog_id))
    catalog = api.get_tool(catalog_id)
    if index_name in catalog.indexes():
        logger.info("Index '{}' already in catalog '{}' [SKIP]"
                    .format(index_name, catalog_id))
        return
    catalog.addIndex(index_name, index_metatype)
    logger.info("Indexing new index '{}' ...".format(index_name))
    catalog.manage_reindexIndex(index_name)


def commit_transaction(portal):
    start = time.time()
    logger.info("Commit transaction ...")
    transaction.commit()
    end = time.time()
    logger.info("Commit transaction ... Took {:.2f}s [DONE]"
                .format(end - start))


def remove_supplyorder_action_from_clients(portal):
    logger.info("Removing 'orders' action from clients ...")
    type_info = portal.portal_types.getTypeInfo("Client")
    actions = map(lambda action: action.id, type_info._actions)
    for index, action in enumerate(actions, start=0):
        if action == "orders":
            type_info.deleteActions([index])
            break
    logger.info("Removing 'orders' action from clients [DONE]")


def remove_supplyorder_folder(portal):
    logger.info("Removing supplyorder folder ...")
    supplyorders = portal.get("supplyorders")
    if supplyorders:
        portal.manage_delObjects(supplyorders.getId())
    logger.info("Removing supplyorder folder [DONE]")


def remove_all_supplyorders(portal):
    logger.info("Removing all supplyorders ...")
    num = 0
    clients = portal.clients.objectValues()

    for client in clients:
        cid = client.getId()
        logger.info("Deleting supplyorders of client {}...".format(cid))
        sids = client.objectIds(spec="SupplyOrder")
        for sid in sids:
            num += 1
            # bypass security checks
            try:
                client._delObject(sid)
                logger.info("#{}: Deleted supplyorder '{}' of client '{}'"
                            .format(num, sid, cid))
            except Exception:
                logger.error("Cannot delete supplyorder '{}': {}"
                             .format(sid, traceback.format_exc()))
            if num % 1000 == 0:
                commit_transaction(portal)

    logger.info("Removed a total of {} supplyorders, committing...".format(num))
    commit_transaction(portal)


def remove_supplyorder_typeinfo(portal):
    logger.info("Remove supplyorder typeinfo ...")
    pt = portal.portal_types
    for t in ["SupplyOrder", "SupplyOrderFolder"]:
        if t in pt.objectIds():
            pt.manage_delObjects(t)

    logger.info("Remove supplyorder typeinfo [DONE]")


def remove_supplyorder_workflow(portal):
    logger.info("Remove supplyorder workflow ...")
    wf_tool = portal.portal_workflow
    wf = wf_tool.get("senaite_supplyorder_workflow")
    if wf is not None:
        wf_tool.manage_delObjects(wf.getId())
    logger.info("Remove supplyorder workflow [DONE]")


def remove_stale_metadata(portal):
    logger.info("Removing stale metadata ...")
    for catalog, column in METADATA_TO_REMOVE:
        del_metadata(catalog, column)
    logger.info("Removing stale metadata ... [DONE]")


def del_metadata(catalog_id, column):
    logger.info("Removing '{}' metadata from '{}' ..."
                .format(column, catalog_id))
    catalog = api.get_tool(catalog_id)
    if column not in catalog.schema():
        logger.info("Metadata '{}' not in catalog '{}' [SKIP]"
                    .format(column, catalog_id))
        return
    catalog.delColumn(column)


def resolve_attachment_due(portal):
    logger.info("Resolving objects in 'attachment_due' status ...")

    # The only objects that can be in attachment_due are worksheets
    query = {"portal_type": "Worksheet", "review_state": "attachment_due"}
    for worksheet in api.search(query, CATALOG_WORKSHEET_LISTING):
        changeWorkflowState(worksheet, "bika_worksheet_workflow",
                            "to_be_verified", action="submit")

    logger.info("Resolving objects in 'attachment_due' status [DONE]")
