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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.


from bika.lims import api
from bika.lims.interfaces import IInvalidated
from bika.lims.utils import tmpID
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContent
from senaite.core import logger
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import WORKSHEET_CATALOG
from senaite.core.catalog.analysis_catalog import INDEXES as ANALYSIS_INDEXES
from senaite.core.config import PROJECTNAME as product
from senaite.core.config.worksheet import DEFAULT_WORKSHEET_LAYOUT
from senaite.core.interfaces import IContentMigrator
from senaite.core.interfaces.catalog import ISenaiteCatalogObject
from senaite.core.registry import set_registry_record
from senaite.core.setuphandlers import add_catalog_column
from senaite.core.setuphandlers import add_catalog_index
from senaite.core.setuphandlers import add_dexterity_items
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

version = "2.7.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

REMOVE_AT_TYPES = [
    "Worksheet",
    "WorksheetFolder",
]

PORTAL_FOLDER_ITEMS = {
    # ID: ID, Title, FTI
    "worksheets": ("worksheets", "Worksheets", "Worksheets"),
}


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


def get_destination_folder(folder_id):
    """Returns the folder with the given name
    """
    portal = api.get_portal()
    folder = portal.get(folder_id)
    if not folder:
        logger.info(
            "Folder '{}' not found and will be create.".format(folder_id))
        if folder_id not in PORTAL_FOLDER_ITEMS:
            raise Exception(
                "Not found data for create folder by: {}".format(folder_id))

        folder_data = PORTAL_FOLDER_ITEMS[folder_id]
        add_dexterity_items(portal, folder_data)
        folder = portal.get(folder_id)
    return folder


def copy_from_bika_setup_to_senaite_registry(fields):
    """Copy fields from BIKA Setup content to SENAITE registry

    :param fields: list of tuple (old_field, new_field, default_value)
    """
    bika_setup = api.get_bika_setup()
    for old, new, default_value in fields:
        value = bika_setup.getField(old_field).get(bika_setup)
        if not value:
            value = default_value
        logger.info("Copy field {}({}) -> {}".format(old, value, new))
        set_registry_record(new, value)


@upgradestep(product, version)
def import_rolemap(tool):
    """Import rolemap step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    setup.runImportStepFromProfile(profile, "rolemap")


@upgradestep(product, version)
def import_registry(tool):
    """Import registry step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    setup.runImportStepFromProfile(profile, "plone.app.registry")


def mark_invalidated_samples(tool):
    """Mark invalidated samples with IInvalidated interface
    """
    logger.info("Mark invalidated samples as IInvalidated ...")
    query = {"portal_type": "AnalysisRequest", "review_state": "invalid"}
    brains = api.search(query, SAMPLE_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Flagging invalidated samples {0}/{1}"
                        .format(num, total))

        sample = api.get_object(brain)
        if IInvalidated.providedBy(sample):
            continue

        alsoProvides(sample, IInvalidated)
        sample.reindexObject()
        sample._p_deactivate()

    logger.info("Mark invalidated samples as IInvalidated [DONE]")


@upgradestep(product, version)
def upgrade_catalog_modified_index(tool):
    """Update modified index in catalog
    """
    logger.info("Upgrade catalog modified index ...")
    portal = api.get_portal()

    # Get all catalogs that implement ISenaiteCatalogObject
    objects = portal.objectValues()
    cats = [cat for cat in objects if ISenaiteCatalogObject.providedBy(cat)]

    # Add the `modified` index and metadata
    for cat in cats:
        add_catalog_index(cat, "modified", "", "DateIndex")
        add_catalog_column(cat, "modified")

    logger.info("Upgrade catalog modified index [DONE]")
    logger.warn(
        "You may need to manually reindex the 'modified' index in existing "
        "catalogs as required."
    )


def update_analysis_catalog_indexes(tool):
    """Update analysis catalog indexes
    """
    logger.info("Update analysis catalog indexes ...")
    to_reindex = []
    catalog = api.get_tool(ANALYSIS_CATALOG)
    for record in ANALYSIS_INDEXES:
        if add_catalog_index(catalog, *record):
            to_reindex.append(record[0])

    for index_id in to_reindex:
        logger.info("Reindexing index '%s'" % index_id)
        catalog.reindexIndex(index_id, api.get_request())

    logger.info("Update analysis catalog indexes [DONE]")


@upgradestep(product, version)
def migrate_worksheets_to_dx(tool):
    """Convert existing worksheet templates to Dexterity
    """
    logger.info("Convert Worksheet's to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    registry_fields = [
        ("WorksheetLayout", "worksheet_layout", DEFAULT_WORKSHEET_LAYOUT),
        ("RestrictWorksheetUsersAccess",
         "restrict_worksheet_users_access", True),
        ("RestrictWorksheetManagement", "restrict_worksheet_management", True),
        ("ScientificNotationReport", "scientific_notation_report", "1"),
    ]
    copy_from_bika_setup_to_senaite_registry(registry_fields)

    # Find all Worksheet objects
    query = {
        "portal_type": "Worksheet",
    }
    brains = api.search(query, WORKSHEET_CATALOG)
    total = len(brains)
    logger.info("Found {} Worksheet objects to migrate".format(total))

    destination_folder = get_destination_folder("worksheets")

    for num, brain in enumerate(brains, start=1):
        # Get the object
        worksheet = api.get_object(brain)

        if num % 100 == 0:
            logger.info(
                "Progress: {}/{} worksheets migrated".format(num, total))
        migrate_worksheet_to_dx(worksheet, destination_folder)

    logger.info("Convert Worksheet's to Dexterity [DONE]")


def migrate_worksheet_to_dx(src, destination):
    """Migrate a Worksheet to DX in destination folder

    :param src: The source AT object
    :param destination: The destination folder
    """
    # Create the object if it does not exist yet
    src_id = src.getId()
    target_id = src_id

    target = destination.get(target_id)
    if not target:
        # Don't use the api to skip the auto-id generation
        target = createContent("Worksheet", id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.description = api.safe_unicode(src.Description() or "")
    target.worksheet_template = src.getRawWorksheetTemplate()
    target.method = src.getRawMethod()
    target.analyst = src.getAnalystName()
    target.instrument = src.getRawInstrument()
    target.results_layout = src.getResultsLayout()
    target.analyses = src.getAnalysesUIDs()
    if hasattr(src, "replaced_by"):
        target.replaced_by = getattr(src, "replaced_by")
    if hasattr(src, "replaces_rejected_worksheet"):
        replaces_uid = getattr(src, "replaces_rejected_worksheet")
        target.replaces_rejected_worksheet = replaces_uid
    # layout
    # remarks

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter((src, target), interface=IContentMigrator)

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

    logger.info("Migrated Worksheet from %s -> %s" % (src, target))
