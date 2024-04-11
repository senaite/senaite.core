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

from Acquisition import aq_parent
from bika.lims import api
from bika.lims.api.snapshot import disable_snapshots
from bika.lims.utils import tmpID
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContent
from Products.Archetypes.utils import getRelURL
from senaite.core import logger
from senaite.core.api.catalog import reindex_index
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import CLIENT_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.config import PROJECTNAME as product
from senaite.core.interfaces import IContentMigrator
from senaite.core.setuphandlers import add_senaite_setup_items
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.setuphandlers import setup_other_catalogs
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.upgrade.utils import copy_snapshots
from senaite.core.upgrade.utils import delete_object
from senaite.core.upgrade.utils import uncatalog_object
from senaite.core.workflow import ANALYSIS_WORKFLOW
from zope.component import getMultiAdapter

version = "2.6.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

REMOVE_AT_TYPES = [
    "AnalysisProfiles",
    "AnalysisProfile",
    "Department",
    "Departments",
    "SampleCondition",
    "SampleConditions",
    "SampleMatrix",
    "SampleMatrices",
    "SamplePreservation",
    "SamplePreservations",
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
    setup.runImportStepFromProfile(profile, "plone.app.registry")


def setup_client_catalog(tool):
    """Setup client catalog
    """
    logger.info("Setup Client Catalog ...")
    portal = api.get_portal()

    setup_core_catalogs(portal)
    client_catalog = api.get_tool(CLIENT_CATALOG)
    client_catalog.clearFindAndRebuild()

    logger.info("Setup Client Catalog [DONE]")
