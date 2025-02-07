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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from datetime import timedelta

from Acquisition import aq_parent
from bika.lims import api
from bika.lims.api import UID_CATALOG
from bika.lims.api.snapshot import disable_snapshots
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.utils import tmpID
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContent
from plone.namedfile import NamedBlobFile
from Products.Archetypes.utils import getRelURL
from Products.CMFCore.permissions import View
from senaite.core import logger
from senaite.core.api import workflow as wapi
from senaite.core.api.catalog import del_index
from senaite.core.api.catalog import reindex_index
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import CLIENT_CATALOG
from senaite.core.catalog import CONTACT_CATALOG
from senaite.core.catalog import REPORT_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.catalog import SENAITE_CATALOG
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.config import PROJECTNAME as product
from senaite.core.interfaces import IContentMigrator
from senaite.core.setuphandlers import add_senaite_setup_items
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.setuphandlers import setup_other_catalogs
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import copy_snapshots
from senaite.core.upgrade.utils import del_metadata
from senaite.core.upgrade.utils import delete_object
from senaite.core.upgrade.utils import permanently_allow_type_for
from senaite.core.upgrade.utils import uncatalog_brain
from senaite.core.upgrade.utils import uncatalog_object
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.workflow import ANALYSIS_WORKFLOW
from senaite.core.workflow import LABCONTACT_WORKFLOW
from senaite.core.schema.addressfield import BILLING_ADDRESS
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.schema.addressfield import POSTAL_ADDRESS
from zope.component import getMultiAdapter

version = "2.6.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

REMOVE_AT_TYPES = [
    "AnalysisProfile",
    "AnalysisProfiles",
    "Department",
    "Departments",
    "SampleCondition",
    "SampleConditions",
    "SampleMatrices",
    "SampleMatrix",
    "SamplePoint",
    "SamplePoints",
    "SamplePreservation",
    "SamplePreservations",
    "SampleTemplate",
    "SampleTemplates",
    "Manufacturer",
    "Manufacturers",
    "ContainerType",
    "ContainerTypes",
    "SubGroup",
    "SubGroups",
    "StorageLocation",
    "StorageLocations",
    "InstrumentType",
    "InstrumentTypes",
    "SamplingDeviation",
    "SamplingDeviations",
    "BatchLabel",
    "BatchLabels",
    "AnalysisCategory",
    "AnalysisCategories",
    "AttachmentType",
    "AttachmentTypes",
    "LabProduct",
    "LabProducts",
    "Supplier",
    "Suppliers",
    "SampleType",
    "SampleTypes",
    "WorksheetTemplate",
    "WorksheetTemplates",
]

CONTENT_ACTIONS = [
    # portal_type, action
    ("Client", {
        "id": "templates",
        "name": "Sample Templates",
        "action": "string:${object_url}/@@sampletemplates",
        "permission": View,
        "category": "object",
        "visible": True,
        "icon_expr": "",
        "link_target": "",
        "condition": "",
        "insert_after": "profiles",
    }),
]


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_at_portal_types(tool):
    """Remove obsolete AT portal type information
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

    # remove from AT's factory tool as well. This is necessary for the AT's
    # factory_tool to not shortcut `createObject?type_name=` on object creation
    ft = api.get_tool("portal_factory")
    at_types = ft.getFactoryTypes().keys()
    at_types = filter(lambda name: name not in REMOVE_AT_TYPES, at_types)
    ft.manage_setPortalFactoryTypes(listOfTypeIds=at_types)

    logger.info("Remove AT types from portal_types tool ... [DONE]")


def migrate_to_dx(at_portal_type, origin, dest, schema_mapping,
                  dx_portal_type=None):
    """Migrates Setup AT contents to Dexterity
    """
    logger.info("Migrating {} to Dexterity ...".format(at_portal_type))

    if not dx_portal_type:
        # keeps same portal type name as the AT type
        dx_portal_type = at_portal_type

    # copy items from old -> new container
    objects = origin.objectValues()
    for src in objects:
        if api.get_portal_type(src) != at_portal_type:
            logger.error("Not a '{}' object: {}".format(at_portal_type, src))
            continue

        # Create the object if it does not exist yet
        src_id = src.getId()
        target = dest.get(src_id)
        if not target:
            # Don' use the api to skip the auto-id generation
            target = createContent(dx_portal_type, id=src_id)
            dest._setObject(src_id, target)
            target = dest._getOb(src_id)

        # Migrate the contents from AT to DX
        migrator = getMultiAdapter(
            (src, target), interface=IContentMigrator)
        migrator.migrate(schema_mapping, delete_src=True)

    logger.info("Migrating {} to Dexterity [DONE]".format(at_portal_type))


def get_setup_folder(folder_id):
    """Returns the folder from setup with the given name
    """
    setup = api.get_senaite_setup()
    folder = setup.get(folder_id)
    if not folder:
        portal = api.get_portal()
        add_senaite_setup_items(portal)
        folder = setup.get(folder_id)
    return folder


@upgradestep(product, version)
def migrate_samplematrices_to_dx(tool):
    """Converts existing sample matrices to Dexterity
    """
    logger.info("Convert SampleMatrices to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_samplematrices")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("samplematrices")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("SampleMatrix", origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert SampleMatrices to Dexterity [DONE]")


@upgradestep(product, version)
def migrate_preservations_to_dx(tool):
    """Converts existing sample preservations to Dexterity
    """
    logger.info("Convert Preservations to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_preservations")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("samplepreservations")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
        "Category": ("getCategory", "category", ""),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("Preservation", origin, destination, schema_mapping,
                  dx_portal_type="SamplePreservation")

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert Preservations to Dexterity [DONE]")


@upgradestep(product, version)
def migrate_sampleconditions_to_dx(tool):
    """Converts existing sample conditions to Dexterity
    """
    logger.info("Convert SampleConditions to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_sampleconditions")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("sampleconditions")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("SampleCondition", origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert SampleConditions to Dexterity [DONE]")


@upgradestep(product, version)
def migrate_departments_to_dx(tool):
    """Converts existing departments to Dexterity
    """
    logger.info("Convert Departments to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_departments")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("departments")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
        "DepartmentID": ("getDepartmentID", "department_id", ""),
        "Manager": ("getManager", "manager", None),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("Department", origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    logger.info("Convert Departments to Dexterity [DONE]")


@upgradestep(product, version)
def migrate_analysisprofiles_to_dx(tool):
    """Converts existing analysis profiles to Dexterity
    """
    logger.info("Convert Analysis Profiles to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # ensure new indexes
    portal = api.get_portal()
    setup_core_catalogs(portal)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_analysisprofiles")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("analysisprofiles")

    # un-catalog the old container
    uncatalog_object(origin)

    # copy items from old -> new container
    objects = origin.objectValues()
    for src in objects:
        migrate_profile_to_dx(src, destination)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert Analysis Profiles to Dexterity [DONE]")


def migrate_profile_to_dx(src, destination=None):
    """Migrate an AT profile to DX in the destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder of
                        the source object is taken
    """
    # migrate the contents from the old AT container to the new one
    portal_type = "AnalysisProfile"

    if api.get_portal_type(src) != portal_type:
        logger.error("Not a '{}' object: {}".format(portal_type, src))
        return

    # Create the object if it does not exist yet
    src_id = src.getId()
    target_id = src_id

    # check if we migrate within the same folder
    if destination is None:
        # use a temporary ID for the migrated content
        target_id = tmpID()
        # set the destination to the source parent
        destination = api.get_parent(src)

    target = destination.get(target_id)
    if not target:
        # Don' use the api to skip the auto-id generation
        target = createContent(portal_type, id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.description = api.safe_unicode(src.Description() or "")
    target.profile_key = api.safe_unicode(src.getProfileKey() or "")

    # services is now a records field containing the selected service and
    # the hidden settings
    services = []
    selected_services = src.getService()
    for obj in selected_services:
        uid = api.get_uid(obj)
        service_setting = src.getAnalysisServiceSettings(uid)
        hidden = service_setting.get("hidden", False)
        services.append({
            "uid": uid,
            "hidden": hidden,
        })
    target.services = services
    target.commercial_id = api.safe_unicode(src.getCommercialID())
    target.use_analysis_profile_price = bool(
        src.getUseAnalysisProfilePrice())
    target.analysis_profile_price = api.to_float(
        src.getAnalysisProfilePrice(), 0.0)
    target.analysis_profile_vat = api.to_float(
        src.getAnalysisProfileVAT(), 0.0)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    logger.info("Migrated Profile from %s -> %s" % (src, target))


def remove_at_departments_setup_folder(tool):
    """Remove the old departments setup folder
    """
    logger.info("Remove AT Departments Setup Folder ...")
    bikasetup = api.get_setup()

    old = bikasetup.get("bika_departments")
    if old:
        delete_object(old)
    logger.info("Remove AT Departments Setup Folder [DONE]")


@upgradestep(product, version)
def fix_analysis_reject_permission(tool):
    """Fixes the analysis reject permission, that was not defined at top-level
    """
    portal = api.get_portal()
    setup = portal.portal_setup

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # Reimport rolemap.xml
    setup.runImportStepFromProfile(profile, "rolemap")

    # Reimport workflows
    setup.runImportStepFromProfile(profile, "workflow")

    # Update role mappings of analyses, but only for those analyses that are
    # in a state from which the new permission can apply
    statuses = ["unassigned", "assigned", "to_be_verified"]
    logger.info("Updating role mappings: Analysis ({}) ..."
                .format(", ".join(statuses)))
    query = {"portal_type": "Analysis", "review_state": statuses}
    brains = api.search(query, ANALYSIS_CATALOG)
    update_workflow_role_mappings(ANALYSIS_WORKFLOW, brains)
    logger.info("Updating role mappings: Analysis ({}) [DONE]"
                .format(", ".join(statuses)))


def update_workflow_role_mappings(wf_id, objs_or_brains):
    """Update the workflow role mappings for the given objects or brains
    """
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    total = len(objs_or_brains)

    for num, obj_brain in enumerate(objs_or_brains):
        if num and num % 100 == 0:
            logger.info("Updating role mappings {0}/{1}".format(num, total))

        obj = api.get_object(obj_brain)
        workflow.updateRoleMappingsFor(obj)
        obj.reindexObject()
        obj._p_deactivate()


def remove_folders_snapshots(tool):
    """Removes the auditlog snapshots for portal and setup folders and remove
    the IAuditable marker interface as well
    """
    logger.info("Removing snapshots from portal and setup folders ...")
    portal = tool.aq_inner.aq_parent
    bika_setup = api.get_setup()
    setup = api.get_senaite_setup()

    # pick all folders "folders"
    folders = portal.objectValues()
    folders += bika_setup.objectValues()
    folders += setup.objectValues()

    # remove non-objects
    folders = filter(api.is_object, folders)
    folders = list(set(folders))

    # remove setup folders (they hold settings as fields)
    skip = [bika_setup, setup]
    folders = filter(lambda folder: folder not in skip, folders)

    # disable auditlog and snapshots
    map(disable_snapshots, folders)

    logger.info("Removing snapshots from portal and setup folders [DONE]")


def add_path_index_to_uid_catalog(tool):
    """Add path index to UID catalog
    """
    logger.info("Setup path index for UID catalog ...")
    setup_other_catalogs(api.get_portal())
    logger.info("Setup path index for UID catalog [DONE]")


def cleanup_uid_catalog(tool):
    """Clean up duplicates and orphane catalog brains
    """
    logger.info("Cleanup UID catalog ...")
    # ensure path index ins in UID Catalog
    catalog = api.get_tool("uid_catalog")
    brains = catalog.searchAll()
    total = len(brains)
    mapping = {}
    duplicates = []
    temporaries = []

    for num, brain in enumerate(brains):
        if num and num % 1000 == 0:
            logger.info("Checking catalog brain %s/%s" % (num, total))

        # check for temporary objects
        if api.is_temporary(brain):
            temporaries.append(brain)
            continue

        # check if we found a duplicate
        uid = brain.UID
        duplicate = mapping.get(uid)

        if duplicate is None:
            mapping[uid] = brain
        else:
            obj = api.get_object(brain)
            dup_obj = api.get_object(duplicate)
            if obj != dup_obj:
                # different objects with same UID!
                logger.error("Different objects with same UID: {}".format(uid))
                continue

            # duplicate detected!
            duplicates.append(brain)
            if duplicate not in duplicates:
                duplicates.append(duplicate)

    portal_types = api.get_tool("portal_types")
    type_info = dict(map(lambda ti: (ti.id, ti), portal_types.listTypeInfo()))

    # cleaning duplicates
    for brain in duplicates:
        oid = api.get_id(brain)
        path = api.get_path(brain)
        obj = api.get_object(brain)
        # uncatalog the object for the current path
        logger.info("Uncatalog brain '%s' at '%s'" % (oid, path))
        catalog.uncatalog_object(path)

        # AT objects are catalogued on the relative path
        fti = type_info.get(brain.portal_type)
        if fti.product:
            # catalog the object on the relative path
            rel_url = getRelURL(catalog, obj.getPhysicalPath())
            logger.info("Catalog brain '%s' at '%s'" % (oid, rel_url))
            catalog.catalog_object(obj, rel_url)
        else:
            # catalog the object on the absolute path
            abs_url = "/".join(obj.getPhysicalPath())
            logger.info("Catalog brain '%s' at '%s'" % (oid, abs_url))
            catalog.catalog_object(obj, abs_url)

    # cleaning temporaries
    for brain in temporaries:
        oid = api.get_id(brain)
        path = api.get_path(brain)
        # skip references
        if "at_references" in path:
            continue
        try:
            obj = api.get_object(brain)
            logger.info("Uncatalog brain '%s' at '%s'" % (oid, path))
            catalog.uncatalog_object(path)
            # unindex the temporary object
            obj.unindexObject()
            # delete the temporary object
            opath = api.get_path(obj)
            logger.info("Delete temporary object '%s' at '%s'" % (oid, opath))
            parent = aq_parent(obj)
            parent._delObject(oid, suppress_events=True)
        except api.APIError:
            # remove the catalog brain only
            logger.info("Uncatalog brain '%s' at '%s'" % (oid, path))
            catalog.uncatalog_object(path)

    logger.info("Cleanup UID catalog [DONE]")


@upgradestep(product, version)
def migrate_client_located_analysisprofiles_to_dx(tool):
    """Migrate client located Profiles to DX
    """
    logger.info("Convert Client located Profiles to Dexterity ...")

    portal = api.get_portal()
    clients = portal.clients

    # search for all client located Analysis Profiles
    query = {
        "portal_type": "AnalysisProfile",
        "path": {
            "query": api.get_path(clients),
        }
    }
    brains = api.search(query, SETUP_CATALOG)

    for brain in brains:
        obj = api.get_object(brain)
        # Check if the object contains the AT UID attribute
        at_uid = getattr(obj, "_at_uid", "")
        if not at_uid:
            continue
        migrate_profile_to_dx(obj)

    logger.info("Convert Client located Profiles to Dexterity [DONE]")


def reindex_sampletype_uid(tool):
    """Reindex the sampletype_uid index from setup catalog
    """
    logger.info("Reindexing sampletype_uid index from setup ...")
    reindex_index(SETUP_CATALOG, "sampletype_uid")
    logger.info("Reindexing sampletype_uid index from setup [DONE]")


@upgradestep(product, version)
def import_registry(tool):
    """Import registry step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    setup.runImportStepFromProfile(profile, "plone.app.registry")


@upgradestep(product, version)
def import_actions(tool):
    """Import actions step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "actions")


@upgradestep(product, version)
def import_usersschema(tool):
    """Import usersschema step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "usersschema")


@upgradestep(product, version)
def import_controlpanel(tool):
    """Import usersschema step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "controlpanel")


@upgradestep(product, version)
def import_workflow(tool):
    """Import usersschema step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "workflow")


@upgradestep(product, version)
def migrate_sampletemplates_to_dx(tool):
    """Converts existing sample templates to Dexterity
    """
    logger.info("Convert SampleTemplates to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # ensure new indexes
    portal = api.get_portal()
    setup_core_catalogs(portal)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")
    tool.runImportStepFromProfile(profile, "rolemap")

    # update content actions
    update_content_actions(tool)

    # allow to create the new DX based sample templates below clients
    permanently_allow_type_for("Client", "SampleTemplate")

    # NOTE: Sample templates can be created in setup and client context!
    query = {"portal_type": "ARTemplate"}
    # search all AT based sample templates
    brains = api.search(query, SETUP_CATALOG)
    total = len(brains)

    # get the old setup folder
    old_parent = api.get_setup().get("bika_artemplates")
    # get the new setup folder
    new_parent = get_setup_folder("sampletemplates")

    for num, brain in enumerate(brains):
        # NOTE: we have a different portal type for new DX based templates and
        # don't need any further type checks here.
        old_obj = api.get_object(brain)

        # get the current parent of the object
        current_parent = api.get_parent(old_obj)

        if current_parent == old_parent:
            # parent is the old setup folder -> migrate to the new setup folder
            new_obj = migrate_template_to_dx(old_obj, new_parent)
        else:
            # parent is a subfolder -> migrate within the same folder
            new_obj = migrate_template_to_dx(old_obj)

        logger.info("Migrated sample template {0}/{1}: {2} -> {3}".format(
            num, total, api.get_path(old_obj), api.get_path(new_obj)))

    # remove old AT folder
    if old_parent:
        if len(old_parent) == 0:
            delete_object(old_parent)
        else:
            logger.warn(
                "Old parent folder {} has contents -> skipping deletion"
                .format(old_parent))

    logger.info("Convert SampleTemplates to Dexterity [DONE]")


def migrate_template_to_dx(src, destination=None):
    """Migrate an AT template to DX in the destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder of
                        the source object is taken
    """
    # migrate the contents from the old AT container to the new one
    old_portal_type = "ARTemplate"
    new_portal_type = "SampleTemplate"

    if api.get_portal_type(src) != old_portal_type:
        logger.error("Not a '{}' object: {}".format(old_portal_type, src))
        return

    # Create the object if it does not exist yet
    src_id = src.getId()
    target_id = src_id

    # check if we migrate within the same folder
    if destination is None:
        # use a temporary ID for the migrated content
        target_id = tmpID()
        # set the destination to the source parent
        destination = api.get_parent(src)

    target = destination.get(target_id)
    if not target:
        # Don' use the api to skip the auto-id generation
        target = createContent(new_portal_type, id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.description = api.safe_unicode(src.Description() or "")
    # we set the fields with our custom setters
    target.setSamplePoint(src.getSamplePoint())
    target.setSampleType(src.getSampleType())
    target.setComposite(src.getComposite())
    target.setSamplingRequired(src.getSamplingRequired())
    target.setPartitions(src.getPartitions())
    target.setAutoPartition(src.getAutoPartition())

    # NOTE: Analyses -> Services
    #
    # services is now a records field containing the selected service, the
    # part_id and the hidden setting
    services = []
    for setting in src.getAnalyses():
        uid = setting.get("service_uid")
        if not api.is_uid(uid):
            logger.error("Invalid UID in analysis setting: %s", setting)
            continue
        part_id = setting.get("partition", "")
        # get the hidden settings
        service_setting = src.getAnalysisServiceSettings(uid)
        hidden = service_setting.get("hidden", False)
        services.append({
            "uid": uid,
            "part_id": part_id,
            "hidden": hidden,
        })
    target.setServices(services)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    return target


@upgradestep(product, version)
def migrate_samplepoints_to_dx(tool):
    """Converts existing sample points to Dexterity
    """
    logger.info("Convert SamplePoints to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # ensure new indexes
    portal = api.get_portal()
    setup_core_catalogs(portal)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")
    tool.runImportStepFromProfile(profile, "rolemap")

    # update content actions
    update_content_actions(tool)

    # allow to create the new DX based sample templates below clients
    permanently_allow_type_for("Client", "SamplePoint")

    # NOTE: Sample Points can be created in setup and client context!
    query = {"portal_type": "SamplePoint"}
    # search all AT based sample points
    brains = api.search(query, SETUP_CATALOG)
    total = len(brains)

    # get the old setup folder
    old_setup = api.get_setup().get("bika_samplepoints")
    # get the new setup folder
    new_setup = get_setup_folder("samplepoints")

    # get all objects first
    objects = map(api.get_object, brains)
    for num, obj in enumerate(objects):
        if api.is_dexterity_content(obj):
            # migrated already
            continue

        # get the current parent of the object
        origin = api.get_parent(obj)

        # get the destination container
        if origin == new_setup:
            # migrated already
            continue

        # migrate the object to dexterity
        if origin == old_setup:
            migrate_samplepoint_to_dx(obj, new_setup)
        else:
            migrate_samplepoint_to_dx(obj)

        logger.info("Migrated sample point {0}/{1}: {2} -> {3}".format(
            num, total, api.get_path(obj), api.get_path(obj)))

    if old_setup:
        # remove old AT folder
        if len(old_setup) == 0:
            delete_object(old_setup)
        else:
            logger.warn("Cannot remove {}. Is not empty".format(old_setup))

    logger.info("Convert SamplePoints to Dexterity [DONE]")


@upgradestep(product, version)
def migrate_manufacturers_to_dx(tool):
    """Converts existing manufacturers to Dexterity
    """
    logger.info("Convert Manufacturers to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_manufacturers")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("manufacturers")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("Manufacturer", origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert Manufacturers to Dexterity [DONE]")


@upgradestep(product, version)
def migrate_instrumenttypes_to_dx(tool):
    """Converts existing instrument types to Dexterity
    """
    logger.info("Convert Instrument Types to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_instrumenttypes")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("instrumenttypes")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("InstrumentType",
                  origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert Instrument Types to Dexterity [DONE]")


@upgradestep(product, version)
def migrate_storagelocations_to_dx(tool):
    """Converts existing storage locations to Dexterity
    """
    logger.info("Convert StorageLocations to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_storagelocations")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("storagelocations")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
        "SiteTitle": ("getSiteTitle", "site_title", ""),
        "SiteCode": ("getSiteCode", "site_code", ""),
        "SiteDescription": ("getSiteDescription", "site_description", ""),
        "LocationTitle": ("getLocationTitle", "location_title", ""),
        "LocationCode": ("getLocationCode", "location_code", ""),
        "LocationDescription": ("getLocationDescription",
                                "location_description", ""),
        "LocationType": ("getLocationType", "location_type", ""),
        "ShelfTitle": ("getShelfTitle", "shelf_title", ""),
        "ShelfCode": ("getShelfCode", "shelf_code", ""),
        "ShelfDescription": ("getShelfDescription", "shelf_description", ""),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("StorageLocation",
                  origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert StorageLocations to Dexterity [DONE]")


@upgradestep(product, version)
def migrate_samplingdeviations_to_dx(tool):
    """Converts existing sampling deviations to Dexterity
    """
    logger.info("Convert Sampling Deviations to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_samplingdeviations")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("samplingdeviations")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("SamplingDeviation",
                  origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert Sampling Deviations to Dexterity [DONE]")


@upgradestep(product, version)
def migrate_analysiscategories_to_dx(tool):
    """Converts existing analysis categories to Dexterity
    """
    logger.info("Convert Analysis Categories to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_analysiscategories")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("analysiscategories")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
        "Comments": ("Comments", "comments", ""),
        "Department": ("Department", "department", ""),
        "SortKey": ("SortKey", "sort_key", ""),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("AnalysisCategory",
                  origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert Analysis Categories to Dexterity [DONE]")


def migrate_samplepoint_to_dx(src, destination=None):
    """Migrates a Sample Point to DX in destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder of
                        the source object is taken
    """

    # Create the object if it does not exist yet
    src_id = src.getId()
    target_id = src_id

    # check if we migrate within the same folder
    if destination is None:
        # use a temporary ID for the migrated content
        target_id = tmpID()
        # set the destination to the source parent
        destination = api.get_parent(src)

    target = destination.get(target_id)
    if not target:
        # Don' use the api to skip the auto-id generation
        target = createContent("SamplePoint", id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.description = api.safe_unicode(src.Description() or "")

    # we set the fields with our custom setters
    target.setLatitude(src.getLatitude())
    target.setLongitude(src.getLongitude())
    target.setElevation(src.getElevation())
    target.setSampleTypes(src.getRawSampleTypes())
    target.setComposite(src.getComposite())

    # attachment file
    attachment = src.getAttachmentFile()
    if attachment:
        filename = attachment.filename
        new_attachment = NamedBlobFile(data=attachment.data,
                                       filename=api.safe_unicode(filename),
                                       contentType=attachment.content_type)
        target.setAttachmentFile(new_attachment)

    # sampling frequency
    freq = dict.fromkeys(["days", "hours", "minutes", "seconds"], 0)
    freq.update(src.getSamplingFrequency() or {})
    freq = dict([(key, api.to_int(val, 0)) for key, val in freq.items()])
    freq = timedelta(**freq)
    target.setSamplingFrequency(freq)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    return target


@upgradestep(product, version)
def migrate_containertypes_to_dx(tool):
    """Converts existing container types to Dexterity
    """
    logger.info("Convert ContainerTypes to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_containertypes")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("containertypes")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("ContainerType", origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert ContainerTypes to Dexterity [DONE]")


@upgradestep(product, version)
def update_typeinfo_subgroups_fix(tool):
    """Fix sub groups typeinfo
    """

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")


@upgradestep(product, version)
def migrate_subgroups_to_dx(tool):
    """Converts existing sub groups to Dexterity
    """
    logger.info("Convert SubGroups to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_subgroups")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("subgroups")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
        "SortKey": ("getSortKey", "sort_key", "")
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("SubGroup", origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert SubGroups to Dexterity [DONE]")


@upgradestep(product, version)
def migrate_batchlabels_to_dx(tool):
    """Converts existing batch labels to Dexterity
    """
    logger.info("Convert ContainerTypes to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_batchlabels")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("batchlabels")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("BatchLabel", origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert BatchLabels to Dexterity [DONE]")


@upgradestep(product, version)
def move_instrumentlocations(tool):
    """Move instrument locations to senaite setup folder
    """

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")

    # get the old container
    origin = api.get_setup().get("instrumentlocations")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("instrumentlocations")

    # un-catalog the old container
    uncatalog_object(origin)

    query = {"portal_type": "InstrumentLocation"}

    brains = api.search(query, SETUP_CATALOG)

    for brain in brains:
        api.move_object(brain, destination, check_constraints=False)

    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Move Instrument Locations [DONE]")


@upgradestep(product, version)
def move_samplecontainers(tool):
    """Move sample containers to senaite setup folder
    """

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")

    # get the old container
    origin = api.get_setup().get("sample_containers")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("samplecontainers")

    # un-catalog the old container
    uncatalog_object(origin)

    query = {"portal_type": "SampleContainer"}

    brains = api.search(query, SETUP_CATALOG)

    for brain in brains:
        api.move_object(brain, destination, check_constraints=False)

    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Move Sample Containers [DONE]")


@upgradestep(product, version)
def migrate_attachmenttypes_to_dx(tool):
    """Converts existing attachment types to Dexterity
    """
    logger.info("Convert AttachmentTypes to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_attachmenttypes")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("attachmenttypes")

    # un-catalog the old container
    uncatalog_object(origin)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
    }

    # migrate the contents from the old AT container to the new one
    migrate_to_dx("AttachmentType", origin, destination, schema_mapping)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert AttachmentTypes to Dexterity [DONE]")


@upgradestep(product, version)
def move_dynamicanalysisspecs(tool):
    """Move dynamic analysis specs to senaite package
    """

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")

    # get the old container
    origin = api.get_setup().get("dynamic_analysisspecs")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("dynamicanalysisspecs")

    # un-catalog the old container
    uncatalog_object(origin)

    query = {"portal_type": "DynamicAnalysisSpec"}

    brains = api.search(query, SETUP_CATALOG)

    for brain in brains:
        api.move_object(brain, destination, check_constraints=False)

    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Move Dynamic Analysis Specs [DONE]")


@upgradestep(product, version)
def move_interpretationtemplates(tool):
    """Move sample interpretation templates to senaite setup folder
    """

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")

    # get the old container
    origin = api.get_setup().get("interpretation_templates")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("interpretationtemplates")

    # un-catalog the old container
    uncatalog_object(origin)

    query = {"portal_type": "InterpretationTemplate"}

    brains = api.search(query, SETUP_CATALOG)

    for brain in brains:
        api.move_object(brain, destination, check_constraints=False)

    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Move Interpretation Templates [DONE]")


@upgradestep(product, version)
def migrate_suppliers_to_dx(tool):
    """Converts suppliers to Dexterity
    """
    logger.info("Convert Suppliers to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    origin = api.get_setup().get("bika_suppliers")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("suppliers")

    # un-catalog the old container
    uncatalog_object(origin)

    query = {"portal_type": "Supplier"}
    # search all AT based suppliers
    brains = api.search(query, SETUP_CATALOG)
    total = len(brains)

    # get all objects first
    objects = map(api.get_object, brains)
    for num, obj in enumerate(objects):
        migrate_supplier_to_dx(obj, destination)

        logger.info("Migrated supplier {0}/{1}: {2} -> {3}".format(
            num, total, api.get_path(obj), api.get_path(obj)))

    if origin:
        # remove old AT folder
        if len(origin) == 0:
            delete_object(origin)
        else:
            logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert Suppliers to Dexterity [DONE]")


def migrate_supplier_to_dx(src_supplier, destination):
    """Migrates a Supplier to DX in destination folder

    :param src_supplier: The source AT object
    :param destination: The destination folder
    """

    # Create the object if it does not exist yet
    src_id = src_supplier.getId()
    target_id = src_id

    target = destination.get(target_id)
    if not target:
        # Don't use the api to skip the auto-id generation
        target = createContent("Supplier", id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src_supplier.getName() or "")

    move_reference_samples(src_supplier, target)

    move_contacts(src_supplier, target)

    # we set the fields with our custom setters
    target.setRemarks(src_supplier.getRemarks())
    target.setWebsite(src_supplier.getWebsite())
    target.setNIB(src_supplier.getNIB())
    target.setIBAN(src_supplier.getIBN())
    target.setSwiftCode(src_supplier.getSWIFTcode())
    target.setLabAccountNumber(src_supplier.getLabAccountNumber())
    target.setTaxNumber(src_supplier.getTaxNumber())
    target.setPhone(src_supplier.getPhone())
    target.setFax(src_supplier.getFax())
    target.setEmail(src_supplier.getEmailAddress())
    target.setAccountType(src_supplier.getAccountType())
    target.setAccountName(src_supplier.getAccountName())
    target.setAccountNumber(src_supplier.getAccountNumber())
    target.setBankName(src_supplier.getBankName())
    target.setBankBranch(src_supplier.getBankBranch())

    # copy addresses: migrate state and district to subdivision's
    postal_address = src_supplier.getPostalAddress()
    if postal_address:
        postal_address["type"] = POSTAL_ADDRESS
        postal_address["subdivision1"] = postal_address.pop("state", "")
        postal_address["subdivision2"] = postal_address.pop("district", "")
        target.setPostalAddress(postal_address)

    physical_address = src_supplier.getPhysicalAddress()
    if physical_address:
        physical_address["type"] = PHYSICAL_ADDRESS
        physical_address["subdivision1"] = physical_address.pop("state", "")
        physical_address["subdivision2"] = physical_address.pop("district", "")
        target.setPhysicalAddress(physical_address)

    billing_address = src_supplier.getBillingAddress()
    if billing_address:
        billing_address["type"] = BILLING_ADDRESS
        billing_address["subdivision1"] = billing_address.pop("state", "")
        billing_address["subdivision2"] = billing_address.pop("district", "")
        target.setBillingAddress(billing_address)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src_supplier, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src_supplier, target)

    # copy the UID
    migrator.copy_uid(src_supplier, target)

    # copy auditlog
    migrator.copy_snapshots(src_supplier, target)

    # copy creators
    migrator.copy_creators(src_supplier, target)

    # copy workflow history
    migrator.copy_workflow_history(src_supplier, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src_supplier, target)

    # copy dates
    migrator.copy_dates(src_supplier, target)

    # uncatalog the source object
    migrator.uncatalog_object(src_supplier)

    # delete the old object
    migrator.delete_object(src_supplier)

    # change the ID *after* the original object was removed
    migrator.copy_id(src_supplier, target)

    return target


def move_reference_samples(source_supplier, target_supplier):
    """
    """
    # search for all reference samples located Supplier
    query_supplier_contacts = {
        "portal_type": "ReferenceSample",
        "path": {
            "query": api.get_path(source_supplier),
        }
    }
    reference_brains = api.search(query_supplier_contacts, SENAITE_CATALOG)
    for brain in reference_brains:
        api.move_object(brain, target_supplier, check_constraints=False)


def move_contacts(source_supplier, target_supplier):
    """
    """
    # search for all contacts located Supplier
    query_supplier_contacts = {
        "portal_type": "SupplierContact",
        "path": {
            "query": api.get_path(source_supplier),
        }
    }
    contact_brains = api.search(query_supplier_contacts, CONTACT_CATALOG)
    for brain in contact_brains:
        api.move_object(brain, target_supplier, check_constraints=False)


def migrate_sampletype_to_dx(src, destination=None):
    """Migrates a Sample Type to DX in destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder of
                        the source object is taken
    """

    # Create the object if it does not exist yet
    src_id = src.getId()
    target_id = src_id

    # check if we migrate within the same folder
    if destination is None:
        # use a temporary ID for the migrated content
        target_id = tmpID()
        # set the destination to the source parent
        destination = api.get_parent(src)

    target = destination.get(target_id)
    if not target:
        # Don' use the api to skip the auto-id generation
        target = createContent("SampleType", id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.description = api.safe_unicode(src.Description() or "")

    # we set the fields with our custom setters
    target.setRetentionPeriod(src.getRetentionPeriod())
    target.setHazardous(src.getHazardous())
    target.setSampleMatrix(src.getSampleMatrix())
    target.setPrefix(src.getPrefix())
    target.setMinimumVolume(src.getMinimumVolume())
    target.setContainerType(src.getContainerType())
    target.setAdmittedStickerTemplates(src.getAdmittedStickerTemplates())

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    return target


@upgradestep(product, version)
def migrate_sampletypes_to_dx(tool):
    """Converts existing Sample Types to Dexterity
    """
    logger.info("Convert SampleTypes to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # ensure new indexes
    portal = api.get_portal()
    setup_core_catalogs(portal)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")
    tool.runImportStepFromProfile(profile, "rolemap")

    # update content actions
    update_content_actions(tool)

    # get the old container
    old_setup = api.get_setup().get("bika_sampletypes")
    if not old_setup:
        # old container is already gone
        return

    # get the destination container
    new_setup = get_setup_folder("sampletypes")

    # NOTE: Sample Points can be created in setup and client context!
    query = {"portal_type": "SampleType"}
    # search all AT based sample points
    brains = api.search(query, SETUP_CATALOG)
    total = len(brains)

    # get all objects first
    objects = map(api.get_object, brains)
    for num, obj in enumerate(objects):
        if api.is_dexterity_content(obj):
            # migrated already
            continue

        # get the current parent of the object
        origin = api.get_parent(obj)

        # get the destination container
        if origin == new_setup:
            # migrated already
            continue

        # migrate the object to dexterity
        if origin == old_setup:
            migrate_sampletype_to_dx(obj, new_setup)
        else:
            migrate_sampletype_to_dx(obj)

        logger.info("Migrated sample type {0}/{1}: {2} -> {3}".format(
            num, total, api.get_path(obj), api.get_path(obj)))

    if old_setup:
        # remove old AT folder
        if len(old_setup) == 0:
            delete_object(old_setup)
        else:
            logger.warn("Cannot remove {}. Is not empty".format(old_setup))

    logger.info("Convert SampleTypes to Dexterity [DONE]")


def reindex_getDueDate(tool):
    """Reindex the getDueDate index from analyses and setup catalog
    """
    logger.info("Reindexing getDueDate index from analyses catalog ...")
    query = {"portal_type": "Analysis"}
    brains = api.search(query, ANALYSIS_CATALOG)
    total = len(brains)
    sample_uids = set()
    for num, brain in enumerate(brains):
        try:
            obj = api.get_object(brain, default=None)
        except AttributeError:
            obj = None
        if obj is None:
            uncatalog_brain(brain)
            continue
        if not IRequestAnalysis.providedBy(obj):
            continue
        if num and num % 100 == 0:
            logger.info(
                "Reindexing getDueDate index from analyses catalog {0}/{1}"
                .format(num, total))
        max_time = obj.MaxTimeAllowed
        if api.to_minutes(**max_time) == 0:
            obj.reindexObject(idxs=['getDueDate'])
            sample = obj.getRequest()
            sample_uid = api.get_uid(sample)
            sample_uids.add(sample_uid)
        obj._p_deactivate()
    logger.info("Reindexing getDueDate index from analyses catalog [DONE]")

    logger.info("Reindexing getDueDate index from samples catalog ...")
    total = len(sample_uids)
    for num, sample_uid in enumerate(sample_uids):
        if num and num % 100 == 0:
            logger.info(
                "Reindexing getDueDate index from samples catalog {0}/{1}"
                .format(num, total))
        obj = api.get_object_by_uid(sample_uid)
        obj.reindexObject(idxs=['getDueDate'])
        obj._p_deactivate()
    logger.info("Reindexing getDueDate index from samples catalog [DONE]")


def update_content_actions(tool):
    logger.info("Update content actions ...")
    portal_types = api.get_tool("portal_types")
    for record in CONTENT_ACTIONS:
        portal_type, action = record
        type_info = portal_types.getTypeInfo(portal_type)
        action_id = action.get("id")
        # remove any previous added actions with the same ID
        _remove_action(type_info, action_id)
        # only remove the content action
        if action.get("remove", False):
            logger.info("Removed action '%s'", action_id)
            continue
        # pop out the position info
        insert_after = action.pop("insert_after", None)
        # add the action
        type_info.addAction(**action)
        # sort the action to the right position
        actions = type_info._cloneActions()
        action_ids = map(lambda a: a.id, actions)
        if insert_after in action_ids:
            ref_index = action_ids.index(insert_after)
            index = action_ids.index(action_id)
            action = actions.pop(index)
            actions.insert(ref_index + 1, action)
            type_info._actions = tuple(actions)

        logger.info("Added action id '%s' to '%s'",
                    action_id, portal_type)
    logger.info("Update content actions [DONE]")


def _remove_action(type_info, action_id):
    """Removes the action id from the type passed in
    """
    actions = map(lambda action: action.id, type_info._actions)
    if action_id not in actions:
        return True
    index = actions.index(action_id)
    type_info.deleteActions([index])
    return _remove_action(type_info, action_id)


def setup_client_catalog(tool):
    """Setup client catalog
    """
    logger.info("Setup Client Catalog ...")
    portal = api.get_portal()

    setup_core_catalogs(portal)
    client_catalog = api.get_tool(CLIENT_CATALOG)
    client_catalog.clearFindAndRebuild()

    logger.info("Setup Client Catalog [DONE]")


def setup_result_types(tool):
    """Setup analysis/service result types
    """
    portal_types = ["AnalysisService", "Analysis", "RejectAnalysis",
                    "DuplicateAnalysis", "ReferenceAnalysis"]
    cat = api.get_tool(UID_CATALOG)
    brains = cat(portal_type=portal_types)
    total = len(brains)
    for num, brain in enumerate(brains):

        if num and num % 1000 == 0:
            logger.info("Setup result types %s/%s" % (num, total))

        obj = api.get_object(brain)
        if not obj:
            continue

        # check if it was set as a string result
        field = obj.getField("StringResult")
        if not field:
            # https://github.com/senaite/senaite.core/pull/2642
            logger.error("Field 'StringResult' not found on object %s (%s)"
                         % (api.get_path(obj), api.get_uid(obj)))
            continue
        string_result = field.get(obj)

        # get the results options type
        options_field = obj.getField("ResultOptionsType")
        options_type = options_field.get(obj)
        if not options_type:
            # processed already
            obj._p_deactivate()
            continue

        if obj.getResultOptions():
            obj.setResultType(options_type)
        elif string_result:
            obj.setResultType("string")
        else:
            obj.setResultType("numeric")

        # empty the value from the old result options field
        options_field.set(obj, None)
        obj._p_deactivate()


def setup_user_profile(tool):
    """Setup user profile
    """
    logger.info("Setup User Profile ...")
    import_actions(tool)
    import_usersschema(tool)
    import_controlpanel(tool)
    import_workflow(tool)

    # Update rolemappings for contacts/labcontacts to grant the Owner role
    # view/edit permissions
    query = {"portal_type": ["LabContact", "Contact"]}
    brains = api.search(query, CONTACT_CATALOG)
    update_workflow_role_mappings(LABCONTACT_WORKFLOW, brains)

    logger.info("Setup User Profile [DONE]")


def remove_creator_fullname(tool):
    """Remove getCreatorFullName from catalogs
    """
    logger.info("Removing getCreatorFullName from catalogs ...")

    del_index(SAMPLE_CATALOG, "getCreatorFullName")
    del_metadata(SAMPLE_CATALOG, "getCreatorFullName")
    del_metadata(REPORT_CATALOG, "getCreatorFullName")

    logger.info("Removing getCreatorFullName from catalogs [DONE]")


def remove_contact_metadata(tool):
    """Remove contact metadata from sample catalog
    """
    logger.info("Removing contact metadata from catalogs ...")

    del_metadata(SAMPLE_CATALOG, "getContactEmail")
    del_metadata(SAMPLE_CATALOG, "getContactFullName")
    del_metadata(SAMPLE_CATALOG, "getContactUsername")
    del_metadata(SAMPLE_CATALOG, "getContactURL")

    logger.info("Removing contact metadata from catalogs [DONE]")


def remove_sampler_fullname(tool):
    """Remove getSamplerFullName from catalogs
    """
    logger.info("Removing getSamplerFullName from catalogs ...")

    del_index(SAMPLE_CATALOG, "getSamplerFullName")
    del_metadata(SAMPLE_CATALOG, "getSamplerFullName")

    logger.info("Removing getSamplerFullName from catalogs [DONE]")


def migrate_samplepoints_coordinates(tool):
    """Migrates the values from SamplePoint coordinate fields to GPSCoordinates
    """
    logger.info("Migrating coordinates from SamplePoint ...")
    cat = api.get_tool(SETUP_CATALOG)
    brains = cat(portal_type="SamplePoint")
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Processed objects: {}/{}".format(num, total))

        obj = api.get_object(brain)

        # get the value from attributes (once DX fields)
        latitude = getattr(obj, "latitude", None)
        longitude = getattr(obj, "longitude", None)
        if not all([latitude, longitude]):
            # migrated already
            continue

        # set the value to the new field Location
        obj.setLatitude(latitude)
        obj.setLongitude(longitude)

        # remove the attributes for latitude and longitude
        delattr(obj, "latitude")
        delattr(obj, "longitude")

        obj.reindexObject()
        obj._p_deactivate() # noqa

    logger.info("Migrating coordinates from SamplePoint [DONE]")


def remove_category_title_metadata(tool):
    """Remove getCategoryTitle metadata from catalogs
    """
    logger.info("Removing getCategoryTitle metadata from catalogs ...")

    del_metadata(ANALYSIS_CATALOG, "getCategoryTitle")
    del_metadata(SETUP_CATALOG, "getCategoryTitle")

    logger.info("Removing getCategoryTitle metadata from catalogs [DONE]")


def set_referenceable_behavior(tool):
    """Assigns the referenceable behavior to setup folders so they are indexed
    in the UID Catalog
    """
    behavior = "plone.app.referenceablebehavior.referenceable.IReferenceable"
    logger.info("Assigning referenceable behavior to setup folders ...")
    pt = api.get_tool("portal_types")
    setup = api.get_senaite_setup()
    to_fix = [setup] + list(setup.objectValues())
    for obj in to_fix:
        if not api.is_dexterity_content(obj):
            logger.warn("Not a DX folder: %r [SKIP]" % obj)
            continue
        portal_type = api.get_portal_type(obj)
        fti = pt.get(portal_type)
        if behavior not in fti.behaviors:
            logger.info("Adding IReferenceable behavior: %s" % portal_type)
            behaviors = list(fti.behaviors) + [behavior]
            fti.behaviors = tuple(behaviors)

        obj.reindexObject()

    logger.info("Assigning referenceable behavior to setup folders [DONE]")


@upgradestep(product, version)
def migrate_labproducts_to_dx(tool):
    """Converts existing lab products to Dexterity
    """
    logger.info("Convert Lab Products to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_labproducts")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("labproducts")

    # un-catalog the old container
    uncatalog_object(origin)

    # copy items from old -> new container
    objects = origin.objectValues()
    for src in objects:
        migrate_labproduct_to_dx(src, destination)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert Lab Products to Dexterity [DONE]")


def migrate_labproduct_to_dx(src, destination=None):
    """Migrate an AT profile to DX in the destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder of
                        the source object is taken
    """
    # migrate the contents from the old AT container to the new one
    portal_type = "LabProduct"

    if api.get_portal_type(src) != portal_type:
        logger.error("Not a '{}' object: {}".format(portal_type, src))
        return

    # Create the object if it does not exist yet
    src_id = src.getId()
    target_id = src_id

    # check if we migrate within the same folder
    if destination is None:
        # use a temporary ID for the migrated content
        target_id = tmpID()
        # set the destination to the source parent
        destination = api.get_parent(src)

    target = destination.get(target_id)
    if not target:
        # Don' use the api to skip the auto-id generation
        target = createContent(portal_type, id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.description = api.safe_unicode(src.Description() or "")
    target.labproduct_volume = api.safe_unicode(src.getVAT() or "")
    target.labproduct_unit = api.safe_unicode(src.getUnit() or "")
    target.labproduct_price = api.to_float(src.getPrice(), 0.0)
    target.labproduct_vat = api.to_float(src.getVAT(), 0.0)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    logger.info("Migrated LabProduct from %s -> %s" % (src, target))


def remove_creation_date_index(tool):
    logger.info("Removing CreationDate index from catalogs ...")
    index = "CreationDate"
    portal = tool.aq_inner.aq_parent
    for cat in portal.objectValues():
        if not isinstance(cat, BaseCatalog):
            continue
        if index not in cat.indexes():
            continue
        logger.info("Removing CreationDate from {}".format(cat.id))
        del_index(cat, index)

    logger.info("Removing CreationDate index from catalogs [DONE]")


def store_raw_analyses(tool):
    logger.info("Storing analysis UIDs as raw data in samples ...")
    # Rolled back
    # see https://github.com/senaite/senaite.core/pull/2603
    logger.info("Storing analysis UIDs as raw data in samples [DONE]")


def del_raw_analyses(tool):
    logger.info("Remove Analyses raw attribute from samples ...")
    query = {"portal_type": "AnalysisRequest"}
    brains = api.search(query, SAMPLE_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Removing Analyses raw attribute from samples {0}/{1}"
                        .format(num, total))

        sample = api.get_object(brain)
        if hasattr(sample, "Analyses"):
            delattr(sample, "Analyses")

        sample._p_deactivate()

    logger.info("Remove Analyses raw attribute from samples [DONE]")


def ensure_valid_sticker_templates(tool):
    logger.info("Ensure sample types have valid sticker templates ...")
    query = {"portal_type": "SampleType"}
    brains = api.search(query, SETUP_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        logger.info("Ensure sample types have valid sticker templates {0}/{1}"
                    .format(num+1, total))
        obj = api.get_object(brain)
        obj.setAdmittedStickerTemplates(obj.getAdmittedStickerTemplates())
    logger.info("Ensure sample types have valid sticker templates [DONE]")


def remove_is_sample_received_index(tool):
    logger.info("Removing isSampleReceived index from catalogs ...")
    cat = api.get_tool(ANALYSIS_CATALOG)
    del_index(cat, "isSampleReceived")
    logger.info("Removing isSampleReceived index from catalogs [DONE]")


def fix_corrupted_transitions(tool):
    logger.info("Fixing corrupted transitions ...")
    wf_tool = api.get_tool("portal_workflow")
    for wf_id in wf_tool.getWorkflowIds():
        wf = wf_tool.getWorkflowById(wf_id)
        for transition_id, transition in wf.transitions.items():
            after_script = getattr(transition, "after_script_name")
            if after_script in ["None", None]:
                logger.info("Fixing %s.%s" % (wf_id, transition_id))
                wapi.update_transition(transition, after_script="")

    logger.info("Fixing corrupted transitions [DONE]")


def reindex_analysis_categories(tool):
    logger.info("Reindexing analysis categories ...")
    cat = api.get_tool(SETUP_CATALOG)
    for brain in cat(portal_type="AnalysisCategory"):
        obj = brain.getObject()
        logger.info("Reindex analysis category: %r" % obj)
        obj.reindexObject(idxs=["sortable_title"], update_metadata=False)
    logger.info("Reindexing analysis categories [DONE]")


def remove_inactive_services_from_profiles(tool):
    logger.info("Removing inactive services from profiles ...")
    cat = api.get_tool(SETUP_CATALOG)

    # build a list of deactivated services
    services = cat(portal_type="AnalysisService", is_active=False)
    inactive = [api.get_object(service) for service in services]

    # remove inactive services from profiles
    for brain in cat(portal_type="AnalysisProfile"):
        obj = api.get_object(brain)
        for service in inactive:
            obj.remove_service(service)

    logger.info("Removing inactive services from profiles [DONE]")


def migrate_ws_template_to_dx(src, destination):
    """Migrate a WorksheetTemplate to DX in destination folder

    :param src: The source AT object
    :param destination: The destination folder
    """

    # Create the object if it does not exist yet
    src_id = src.getId()
    target_id = src_id

    target = destination.get(target_id)
    if not target:
        # Don't use the api to skip the auto-id generation
        target = createContent("WorksheetTemplate", id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.description = api.safe_unicode(src.Description() or "")
    # we set the fields with our custom setters
    target.setRestrictToMethod(src.getRestrictToMethod())
    target.setInstrument(src.getInstrument())

    # NOTE: Service -> Services
    services = []
    for service in src.getService():
        services.append({
            "uid": api.get_uid(service),
        })
    target.setServices(services)

    # NOTE: Layout -> TemplateLayout
    layout = []
    for num, row in enumerate(src.getLayout()):
        ref_proxy = None
        dup = row.get("dup", None)
        dup = int(dup) if dup else None
        analysis_type = row.get("type", "a")
        blank_ref = []
        control_ref = []

        if analysis_type == "a":
            dup = None
        elif analysis_type == "b":
            blank_ref = row.get("blank_ref", "")
            ref_proxy = blank_ref or None
            dup = None
        elif analysis_type == "c":
            control_ref = row.get("control_ref", "")
            ref_proxy = control_ref or None
            dup = None

        layout.append({
            "pos": int(row.get("pos", num + 1)),
            "type": analysis_type,
            "blank_ref": blank_ref if blank_ref else [],
            "control_ref": control_ref if control_ref else [],
            "reference_proxy": ref_proxy,
            "dup_proxy": dup,
            "dup": dup,
        })
    target.setTemplateLayout(layout)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    return target


@upgradestep(product, version)
def migrate_worksheettemplates_to_dx(tool):
    """Convert existing worksheet templates to Dexterity
    """
    logger.info("Convert Worksheet Templates to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_worksheettemplates")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("worksheettemplates")

    # un-catalog the old container
    uncatalog_object(origin)

    query = {"portal_type": "WorksheetTemplate"}
    # search all AT based suppliers
    brains = api.search(query, SETUP_CATALOG)
    total = len(brains)

    # get all objects first
    objects = map(api.get_object, brains)
    for num, obj in enumerate(objects):
        migrate_ws_template_to_dx(obj, destination)

        logger.info("Migrated WorksheetTemplates {0}/{1}: {2} -> {3}".format(
            num, total, api.get_path(obj), api.get_path(obj)))

    if origin:
        # remove old AT folder
        if len(origin) == 0:
            delete_object(origin)
        else:
            logger.warn("Cannot remove {}. Is not empty".format(origin))

    logger.info("Convert Worksheet Templates to Dexterity [DONE]")


def reindex_specs(tool):
    """Reindex the sampletype_uid and sampletype_title indexes from setup
    catalog for AnalysisSpecs types
    """
    logger.info("Reindexing analysis specifications ...")
    cat = api.get_tool(SETUP_CATALOG)
    for brain in cat(portal_type="AnalysisSpec"):
        obj = brain.getObject()
        logger.info("Reindex analysis spec: %r" % obj)
        obj.reindexObject(idxs=["sampletype_uid", "sampletype_title"])
    logger.info("Reindexing analysis specifications [DONE]")


def reindex_sub_groups(tool):
    logger.info("Reindexing sub group ...")
    cat = api.get_tool(SETUP_CATALOG)
    for brain in cat(portal_type="SubGroup"):
        obj = brain.getObject()
        # ensure float values (was a string field before)
        sort_key = obj.getSortKey()
        if not api.is_floatable(sort_key):
            # api.to_float does not accept `None` as default
            try:
                sort_key = float(sort_key)
            except (ValueError, TypeError):
                sort_key = None
            obj.setSortKey(sort_key)

        logger.info("Reindex sub group: %r" % obj)
        if obj.sort_key:
            obj.sort_key = api.to_float(obj.sort_key, 0.0)
        obj.reindexObject(idxs=["sortable_title"], update_metadata=False)
    logger.info("Reindexing sub groups [DONE]")
