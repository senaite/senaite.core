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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import copy
import re
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
from plone.dexterity.fti import DexterityFTI
from Products.Archetypes.config import UID_CATALOG
from Products.CMFEditions.interfaces import IVersioned
from senaite.core import logger
from senaite.core.config import PROJECTNAME as product
from senaite.core.setuphandlers import _run_import_step
from senaite.core.setuphandlers import setup_markup_schema
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.upgrade.utils import catalog_object
from senaite.core.upgrade.utils import copy_snapshots
from senaite.core.upgrade.utils import delete_object
from senaite.core.upgrade.utils import set_uid
from senaite.core.upgrade.utils import temporary_allow_type
from senaite.core.upgrade.utils import uncatalog_object
from senaite.core.workflow import ANALYSIS_WORKFLOW
from senaite.core.workflow import DUPLICATE_ANALYSIS_WORKFLOW
from senaite.core.workflow import REFERENCE_ANALYSIS_WORKFLOW
from senaite.core.workflow import REFERENCE_SAMPLE_WORKFLOW
from senaite.core.workflow import REJECT_ANALYSIS_WORKFLOW
from senaite.core.workflow import SAMPLE_WORKFLOW
from senaite.core.workflow import WORKSHEET_WORKFLOW
from zope.interface import noLongerProvides

version = "2.0.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

REMOVE_AT_TYPES = [
    "AnalysisRequestsFolder",
    "InstrumentLocation",
    "InstrumentLocations",
    "ReflexRule",
    "ReflexRuleFolder",
]

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

INDEXES_TO_REMOVE = [
    # List of tuples (catalog_name, index_name)
    (CATALOG_ANALYSIS_LISTING, "getMethodUID"),
    (CATALOG_ANALYSIS_LISTING, "isRetest"),
    (CATALOG_ANALYSIS_LISTING, "getSamplePointUID"),
    (CATALOG_ANALYSIS_LISTING, "getParentUID"),
    (CATALOG_ANALYSIS_LISTING, "getOriginalReflexedAnalysisUID"),
]

METADATA_TO_REMOVE = [
    # Only used in Analyses listing and it's behavior is bizarre, probably
    # because is a dict and requires special care with ZODB
    (CATALOG_ANALYSIS_LISTING, "getInterimFields"),
    # No longer used, see https://github.com/senaite/senaite.core/pull/1709/
    (CATALOG_ANALYSIS_LISTING, "getAttachmentUIDs"),
    (CATALOG_ANALYSIS_LISTING, "getInstrumentEntryOfResults"),
    (CATALOG_ANALYSIS_LISTING, "getCalculationUID"),
    (CATALOG_ANALYSIS_LISTING, "getAllowedInstrumentUIDs"),
    (CATALOG_ANALYSIS_LISTING, "getMethodUID"),
    (CATALOG_ANALYSIS_LISTING, "getAllowedMethodUIDs"),
    (CATALOG_ANALYSIS_LISTING, "getInstrumentUID"),
    (CATALOG_ANALYSIS_REQUEST_LISTING, "getSamplePointUID"),
    (CATALOG_ANALYSIS_LISTING, "getParentUID"),
    (CATALOG_ANALYSIS_LISTING, "getParentTitle"),
    (CATALOG_ANALYSIS_LISTING, "isInstrumentValid"),
    (CATALOG_ANALYSIS_LISTING, "getIsReflexAnalysis"),
]

STALE_WORKFLOW_DEFINITIONS = [
    # List of stale workflow definition ids to remove
    "bika_sample_workflow",
]

WORKFLOW_DEFINITIONS_TO_PORT = [
    # List of tuples (source wf_id, destination wf_id, [portal_type,])
    ("bika_analysis_workflow", ANALYSIS_WORKFLOW, ["Analysis", ]),
    ("bika_duplicateanalysis_workflow", DUPLICATE_ANALYSIS_WORKFLOW,
     ["DuplicateAnalysis", ]),
    ("bika_ar_workflow", SAMPLE_WORKFLOW, ["AnalysisRequest", ]),
    ("bika_referencesample_workflow", REFERENCE_SAMPLE_WORKFLOW,
     ["ReferenceSample", ]),
    ("bika_referenceanalysis_workflow", REFERENCE_ANALYSIS_WORKFLOW,
     ["ReferenceAnalysis", ]),
    ("bika_reject_analysis_workflow", REJECT_ANALYSIS_WORKFLOW,
     ["RejectAnalysis", ]),
    ("bika_worksheet_workflow", WORKSHEET_WORKFLOW, ["Worksheet", ]),
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

    # Remove AT types from portal_types tool
    remove_at_portal_types(portal)

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
    setup.runImportStepFromProfile(profile, "repositorytool")
    setup.runImportStepFromProfile(profile, "controlpanel")
    setup.runImportStepFromProfile(profile, "plone.app.registry")
    # run import steps located in bika.lims profiles
    _run_import_step(portal, "rolemap", profile="profile-bika.lims:default")
    _run_import_step(portal, "typeinfo", profile="profile-bika.lims:default")
    # https://github.com/senaite/senaite.core/pull/1730
    _run_import_step(
        portal, "componentregistry", profile="profile-bika.lims:default")

    add_dexterity_setup_items(portal)

    # Published results tab is not displayed to client contacts
    # https://github.com/senaite/senaite.core/pull/1638
    fix_published_results_permission(portal)

    # Port workflow definitions to senaite namespace
    port_workflow_definitions(portal)

    # Remove stale workflow definitions
    remove_stale_workflow_definitions(portal)

    # Update workflow mappings for samples to allow profile editing and fix
    # Add Attachment permission for verified and published status
    update_workflow_mappings_samples(portal)
    update_workflow_mappings_worksheets(portal)

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

    # Remove stale indexes
    remove_stale_indexes(portal)

    # Remove stale metadata
    remove_stale_metadata(portal)

    # Convert Instrument Locations to DX
    # https://github.com/senaite/senaite.core/pull/1705
    convert_instrumentlocations_to_dx(portal)

    # Convert AnalysisRequestsFolder to DX
    # https://github.com/senaite/senaite.core/pull/1739
    convert_analysisrequestsfolder_to_dx(portal)

    # Remove analysis services from CMFEditions auto versioning
    # https://github.com/senaite/senaite.core/pull/1708
    remove_services_from_repositorytool(portal)

    # Resolve objects in attachment_due
    resolve_attachment_due(portal)

    # Migrates the `Calculation` field -> `Calculations`
    # https://github.com/senaite/senaite.core/pull/1719
    migrate_calculations_of_methods(portal)

    # Remove calclation interims from service interims
    # https://github.com/senaite/senaite.core/pull/1719
    migrate_service_interims(portal)

    # Remove reflex rule folder
    # https://github.com/senaite/senaite.core/pull/1728
    delete_reflexrulefolder(portal)

    # Removes the method `notifiyModified` from analyses
    # https://github.com/senaite/senaite.core/pull/1731
    remove_collective_indexing_notify_modified(portal)

    # Resolve attachment image URLs in results interpretations by UID
    migrate_resultsinterpretations_inline_images(portal)

    # Setup markup default and allowed schemas
    setup_markup_schema(portal)

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


def port_workflow_definitions(portal):
    """Ports the workflow definitions to senaite namespace
    """
    logger.info("Porting workflow definitions to senaite namespace ...")
    for source, destination, portal_types in WORKFLOW_DEFINITIONS_TO_PORT:
        port_workflow(portal, source, destination, portal_types)
    logger.info("Porting workflow definitions to senaite namespace [DONE]")


def remove_stale_workflow_definitions(portal):
    """Removes stale workflow definitions
    """
    logger.info("Removing stale workflow definitions ...")
    wf_tool = api.get_tool("portal_workflow")
    for workflow_id in STALE_WORKFLOW_DEFINITIONS:
        if workflow_id in wf_tool:
            logger.info("Removing {}".format(workflow_id))
            wf_tool._delObject(workflow_id)  # noqa

    logger.info("Removing stale workflow definitions [DONE]")


def port_workflow(portal, source, destination, portal_types):
    """Ports the workflow to senaite namespace
    """
    msg = "Porting {} to {}".format(source, destination)
    logger.info("{} ...".format(msg))

    wf_tool = api.get_tool("portal_workflow")
    if source not in wf_tool:
        logger.info("{} does not exist [SKIP]".format(source))
        return

    query = {"portal_type": portal_types}
    brains = api.search(query, UID_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("{0}: {1}/{2}".format(msg, num, total))
        if num and num % 1000 == 0:
            commit_transaction(portal)

        # Override the workflow history
        obj = api.get_object(brain)
        history = obj.workflow_history.get(source)
        if history:
            obj.workflow_history[destination] = copy.deepcopy(history)
            del obj.workflow_history[source]

    # Remove the workflow definition from portal_workflow
    wf_tool = api.get_tool("portal_workflow")
    wf_tool._delObject(source)  # noqa
    logger.info("{} [DONE]".format(msg))


def update_workflow_mappings_samples(portal):
    """Allow to edit analysis profiles and fix AddAttachment permission
    """
    logger.info("Updating role mappings for Samples ...")
    wf_id = "senaite_sample_workflow"
    query = {"portal_type": "AnalysisRequest"}
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    update_workflow_mappings_for(portal, wf_id, brains)
    logger.info("Updating role mappings for Samples [DONE]")


def update_workflow_mappings_worksheets(portal):
    """Fix AddAttachment permission
    """
    logger.info("Updating role mappings for Worksheets ...")
    query = {"portal_type": "Worksheet"}
    brains = api.search(query, CATALOG_WORKSHEET_LISTING)
    update_workflow_mappings_for(portal, WORKSHEET_WORKFLOW, brains)
    logger.info("Updating role mappings for Worksheets [DONE]")


def update_workflow_mappings_for(portal, wf_id, brains):
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating role mappings: {0}/{1}".format(num, total))
        if num and num % 1000 == 0:
            commit_transaction(portal)
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


def remove_stale_indexes(portal):
    logger.info("Removing stale indexes ...")
    for catalog_id, index_name in INDEXES_TO_REMOVE:
        del_index(portal, catalog_id, index_name)
    logger.info("Removing stale indexes ... [DONE]")


def del_index(portal, catalog_id, index_name):
    logger.info("Removing '{}' index from '{}' ..."
                .format(index_name, catalog_id))
    catalog = api.get_tool(catalog_id)
    if index_name not in catalog.indexes():
        logger.info("Index '{}' not in catalog '{}' [SKIP]"
                    .format(index_name, catalog_id))
        return
    catalog.delIndex(index_name)


def remove_at_portal_types(portal):
    """Remove AT portal type information
    """
    logger.info("Remove AT types from portal_types tool ...")
    pt = api.get_tool("portal_types")
    for type_name in REMOVE_AT_TYPES:
        fti = pt.getTypeInfo(type_name)
        # keep DX FTIs
        if isinstance(fti, DexterityFTI):
            logger.info("Type '{}' is already a DX FTI".format(fti))
            continue
        elif not fti:
            # Removed already
            continue
        pt.manage_delObjects(fti.getId())
    logger.info("Remove AT types from portal_types tool ... [DONE]")


def convert_instrumentlocations_to_dx(portal):
    """Converts existing Instrument Locations to Dexterity
    """
    logger.info("Convert Instrument Locations to Dexterity ...")

    old_id = "bika_instrumentlocations"
    new_id = "instrument_locations"
    new_title = "Instrument Locations"

    setup = api.get_setup()
    old = setup.get(old_id)

    # return if the old container is already gone
    if not old:
        return

    # uncatalog the old object
    uncatalog_object(old)

    # get the new container
    new = setup.get(new_id)

    # create the new container if it is not there
    if not new:
        # temporarily allow to create objects in setup
        with temporary_allow_type(setup, "InstrumentLocations") as container:
            new = api.create(
                container, "InstrumentLocations", id=new_id, title=new_title)
        new.reindexObject()

    # copy items from old -> new container
    for src in old.objectValues():
        # extract the old values
        uid = api.get_uid(src)
        title = api.get_title(src)
        description = api.get_description(src)
        # uncatalog the old object
        uncatalog_object(src)
        # create the new DX object and set explicitly the values
        target = api.create(new, "InstrumentLocation", title=title)
        target.description = api.safe_unicode(description)
        # take over the UID
        set_uid(target, uid)
        # copy auditlog
        copy_snapshots(src, target)
        # catalog the new object
        catalog_object(target)

    # copy snapshots for the container
    copy_snapshots(old, new)

    # delete the old object
    delete_object(old)

    logger.info("Convert Instrument Locations to Dexterity ... [DONE]")


def convert_analysisrequestsfolder_to_dx(portal):
    """Converts AnalysisRequestsFolder to Dexterity
    """
    logger.info("Convert AnalysisRequestsFolder to Dexterity ...")

    old_id = "analysisrequests"
    new_id = "samples"
    new_title = "Samples"

    old = portal.get(old_id)

    # return if the old container is already gone
    if not old:
        return

    # uncatalog the old object
    uncatalog_object(old)

    # get the new container
    new = portal.get(new_id)

    # create the new container if it is not there
    if not new:
        # temporarily allow to create objects in setup
        with temporary_allow_type(portal, "Samples") as container:
            new = api.create(container, "Samples", id=new_id, title=new_title)
        new.reindexObject()

    # copy snapshots for the container
    copy_snapshots(old, new)

    # delete the old object
    delete_object(old)

    # Move the object after Clients nav item
    position = portal.getObjectPosition("clients")
    portal.moveObjectToPosition("samples", position + 1)
    portal.plone_utils.reindexOnReorder(portal)

    logger.info("Convert AnalysisRequestsFolder to Dexterity ... [DONE]")


def remove_services_from_repositorytool(portal):
    """Remove Analysis Service from Repository Tool
    """
    logger.info("Remove auto versioning for Analysis Services ...")
    portal_type = "AnalysisService"

    rt = api.get_tool("portal_repository")
    mapping = rt._version_policy_mapping
    mapping.pop(portal_type, None)
    rt._version_policy_mapping = mapping
    versionable_types = rt.getVersionableContentTypes()
    if portal_type in versionable_types:
        versionable_types.remove(portal_type)
        rt.setVersionableContentTypes(versionable_types)

    # Remove marker interface for existing services
    brains = api.search(dict(portal_type="AnalysisService"))
    for brain in brains:
        obj = api.get_object(brain)
        if IVersioned.providedBy(obj):
            noLongerProvides(obj, IVersioned)

    logger.info("Remove auto versioning for Analysis Services ... [DONE]")


def resolve_attachment_due(portal):
    logger.info("Resolving objects in 'attachment_due' status ...")

    # The only objects that can be in attachment_due are worksheets
    query = {"portal_type": "Worksheet", "review_state": "attachment_due"}
    for worksheet in api.search(query, CATALOG_WORKSHEET_LISTING):
        worksheet = api.get_object(worksheet)
        changeWorkflowState(worksheet, WORKSHEET_WORKFLOW,
                            "to_be_verified", action="submit")

    logger.info("Resolving objects in 'attachment_due' status [DONE]")


def migrate_calculations_of_methods(portal):
    logger.info("Migrate Method `Calculation` field ...")
    query = {"portal_type": "Method"}
    for brain in api.search(query, SETUP_CATALOG):
        obj = api.get_object(brain)
        calc_field = obj.getField("Calculation")
        calc = calc_field.get(obj)
        if not calc:
            continue
        calcs_field = obj.getField("Calculations")
        calcs = calcs_field.get(obj)
        if calc not in calcs:
            calcs_field.set(obj, calcs + [calc])
            logger.info(
                "Migrated '{}' in Method '{}' to Calculations Field"
                .format(api.get_title(calc), api.get_title(obj)))
        # flush the old field
        calc_field.set(obj, None)

    logger.info("Migrate Method `Calculation` field ... [DONE]")


def migrate_service_interims(portal):
    logger.info("Remove calculation interims from service interims ...")
    query = {"portal_type": "AnalysisService"}
    for brain in api.search(query, SETUP_CATALOG):
        obj = api.get_object(brain)
        calc = obj.getCalculation()
        if not calc:
            continue
        s_interims = obj.getInterimFields()
        if not s_interims:
            continue
        # cleanup service interims from calculation interims
        c_interims = calc.getInterimFields()
        c_interim_keys = map(lambda i: i.get("keyword"), c_interims)
        new_interims = filter(
            lambda i: i.get("keyword") not in c_interim_keys, s_interims)
        obj.setInterimFields(new_interims)
    logger.info("Remove calculation interims from service interims ... [DONE]")


def delete_reflexrulefolder(portal):
    logger.info("Remove reflex rule folder ...")
    setup = api.get_setup()
    obj_id = "bika_reflexrulefolder"
    if obj_id in setup.objectIds():
        setup._delObject(obj_id)
    logger.info("Remove reflex rule folder ... [DONE]")


def remove_collective_indexing_notify_modified(portal):
    """Removes stale artefact from collective.indexing

    Traceback (innermost last):
        Module ZServer.ZPublisher.Publish, line 151, in publish
        Module ZServer.ZPublisher.Publish, line 393, in commit
        Module transaction._manager, line 257, in commit
        Module transaction._manager, line 135, in commit
        Module transaction._transaction, line 282, in commit
        Module transaction._transaction, line 273, in commit
        Module transaction._transaction, line 465, in _commitResources
        Module transaction._transaction, line 439, in _commitResources
        Module ZODB.Connection, line 489, in commit
        Module ZODB.Connection, line 997, in savepoint
        Module ZODB.Connection, line 546, in _commit
        Module ZODB.Connection, line 578, in _store_objects
        Module ZODB.serialize, line 430, in serialize
        Module ZODB.serialize, line 439, in _dump
    PicklingError: Can't pickle <class 'collective.indexing.indexer.notifyModified'>: import of module collective.indexing.indexer failed  # noqa

    in collective.indexing.indexer:

    def reindex(obj, attributes=None):
        op = getDispatcher(obj, 'reindex')
        if op is not None:
            # prevent update of modification date during deferred reindexing
            od = obj.__dict__
            if not 'notifyModified' in od:
                od['notifyModified'] = notifyModified
            op(obj, attributes or [])
            if 'notifyModified' in od:
                del od['notifyModified']
    """
    logger.info("Remove `notifyModified` method from Analyses ...")

    results = api.search(
        dict(portal_type="Analysis"), CATALOG_ANALYSIS_LISTING)
    total = len(results)
    logger.info("Checking {} Analyses".format(total))

    cleaned = 0
    for num, brain in enumerate(results):
        if num and num % 1000 == 0:
            logger.info("Processed {}/{}".format(num+1, total))
        obj = api.get_object(brain)
        od = obj.__dict__
        if "notifyModified" in od:
            logger.info("Removing 'notifyModified' from {}".format(
                api.get_path(obj)))
            del od["notifyModified"]
            obj._p_changed = 1
            obj.reindexObject()
            cleaned += 1

    logger.info("Cleaned {} Analyes, committing transaction.".format(cleaned))
    transaction.commit()
    logger.info("Remove `notifyModified` method from Analyses ... [DONE]")


def migrate_resultsinterpretations_inline_images(portal):
    """Reolve resultsinterpretation inline images
    """
    logger.info("Migrating results interpretation image links ...")

    IMG_SRC_RX = re.compile(r'<img.*?src="(.*?)"')
    ATT_RX = re.compile(r'attachment-[0-9]+')

    catalog = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    query = {"portal_type": "AnalysisRequest"}
    results = catalog(query)
    count = len(results)

    for num, brain in enumerate(results):
        obj = api.get_object(brain)
        if num and num % 1000 == 0:
            logger.info("Processed {}/{}".format(num, count))
            transaction.commit()
        rid = obj.getResultsInterpretationDepts()
        for ri in rid:
            html = ri.get("richtext")
            image_sources = re.findall(IMG_SRC_RX, html)
            for src in image_sources:
                att_id = re.findall(ATT_RX, src)
                if not att_id:
                    continue
                attachment = obj.aq_parent.get(att_id[0])
                if not attachment:
                    continue
                # convert absolute link to `resolve_attachment` view
                link = "resolve_attachment?uid={}".format(
                    api.get_uid(attachment))
                html = html.replace(src, link)
                logger.info(
                    "Converted image link for sample '{}' from '{}' -> '{}'"
                    .format(obj.getId(), src, link))
                obj._p_changed = True
            ri["richtext"] = html
        obj._p_deactivate()

    transaction.commit()
    logger.info("Migrating results interpretation image links ... [DONE]")
