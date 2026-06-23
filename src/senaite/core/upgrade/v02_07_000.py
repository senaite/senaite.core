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


import json
from datetime import timedelta

import transaction
from bika.lims import api
from bika.lims.api import safe_unicode as u
from bika.lims.api import snapshot as snap_api
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.interfaces import IAuditable
from bika.lims.interfaces import IDetachedPartition
from bika.lims.interfaces import IInvalidated
from bika.lims.utils import tmpID
from persistent.list import PersistentList
from plone.app.blob.field import BlobWrapper
from plone.dexterity.utils import createContent
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.interfaces import INamed
from Products.CMFEditions.interfaces import IVersioned
from senaite.core import logger
from senaite.core.api import dtime
from senaite.core.api.catalog import add_column
from senaite.core.api.catalog import del_column
from senaite.core.api.catalog import del_index
from senaite.core.api.catalog import reindex_index
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import CONTACT_CATALOG
from senaite.core.catalog import REPORT_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.catalog import WORKSHEET_CATALOG
from senaite.core.catalog.analysis_catalog import INDEXES as ANALYSIS_INDEXES
from senaite.core.catalog.client_catalog import CATALOG_ID as CLIENT_CATALOG
from senaite.core.config import PROJECTNAME as product
from senaite.core.interfaces import IContentMigrator
from senaite.core.interfaces.catalog import ISenaiteCatalogObject
from senaite.core.schema.addressfield import BILLING_ADDRESS
from senaite.core.schema.addressfield import NAIVE_ADDRESS
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.schema.addressfield import POSTAL_ADDRESS
from senaite.core.schema.uidreferencefield import get_backref_storage
from senaite.core.setuphandlers import _run_import_step
from senaite.core.setuphandlers import add_catalog_column
from senaite.core.setuphandlers import add_catalog_index
from senaite.core.setuphandlers import add_dexterity_items
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.upgrade.utils import blob_to_named_file
from senaite.core.upgrade.utils import copy_snapshots
from senaite.core.upgrade.utils import delete_object
from senaite.core.upgrade.utils import iter_senaite_catalogs
from senaite.core.upgrade.utils import permanently_allow_type_for
from senaite.core.upgrade.utils import rebuild_index
from senaite.core.upgrade.utils import remove_at_portal_types
from senaite.core.upgrade.utils import uncatalog_object
from senaite.core.upgrade.v02_06_000 import get_setup_folder
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

version = "2.7.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

REMOVE_AT_TYPES = [
    "ARReport",
    "Contact",
    "Laboratory",
    "Calculation",
    "Calculations",
    "Multifile",
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


def drop_client_ordering_annotations(tool):
    """Remove the legacy IOrdering annotations from every Client.

    Clients now use `plone.folder.unordered.UnorderedOrdering` as
    their `IOrdering` adapter, so the previous default-ordering
    annotations are no longer maintained:

      - `plone.folder.ordered.order` — a `PersistentList` of every
        child id, mutated on every `_setObject` via
        `DefaultOrdering.notifyAdded`. On a Client with thousands of
        children this list grows to many tens of thousands of entries
        and, because `PersistentList` has no `_p_resolveConflict()`,
        every concurrent registration on the same Client collided on
        it and the conflict propagated all the way to the
        publisher's retry loop.

      - `plone.folder.ordered.pos` — companion `OIBTree` mapping
        child id -> position. No longer read by anything once the
        adapter is unordered.

    Removing both annotations after the adapter switch frees the
    storage they occupy and removes a stale hot-mutation bucket from
    the ZODB cache. The adapter override is what stops new writes
    from touching them; this step is hygiene.
    """
    ORDER_KEY = "plone.folder.ordered.order"
    POS_KEY = "plone.folder.ordered.pos"

    query = {"portal_type": "Client"}
    brains = api.search(query, CLIENT_CATALOG)
    total = len(brains)
    logger.info(
        "Dropping IOrdering annotations from {} clients".format(total))

    cleaned = 0
    for num, brain in enumerate(brains, start=1):
        client = api.get_object(brain)
        ann = IAnnotations(client)
        had_order = ORDER_KEY in ann
        had_pos = POS_KEY in ann
        if not (had_order or had_pos):
            continue
        ann.pop(ORDER_KEY, None)
        ann.pop(POS_KEY, None)
        client._p_changed = True
        cleaned += 1
        if num % 100 == 0:
            logger.info(
                "  ... processed {}/{} clients ({} cleaned)".format(
                    num, total, cleaned))
            transaction.savepoint()

    logger.info(
        "Dropped IOrdering annotations from {}/{} clients".format(
            cleaned, total))


@upgradestep(product, version)
def add_hazard_categories(tool):
    """Register the hazard categories field and metadata column.

    The new ``hazard_categories`` field on ``SampleType`` (DX)
    and the ``HazardCategories`` field on ``ReferenceDefinition``
    and ``ReferenceSample`` (AT) are picked up automatically by
    the schema machinery. Existing objects default to an empty
    list. The legacy ``Hazardous`` boolean is left untouched.
    Samples (``AnalysisRequest``) inherit their effective
    categories from the SampleType — no per-sample field.

    The vocabulary covers the 9 GHS pictograms plus 10 ISO 7010
    pictograms (biohazard, radioactive, non-ionising radiation,
    electricity, low temperature, hot content, magnetic field,
    hot surface, asphyxiating atmosphere, hot steam) for hazards
    that GHS does not address.

    Hazard pictograms are rendered in listings by reading the
    ``getHazardous`` and ``getHazardCategories`` metadata columns
    from the SampleType brain in the setup catalog (looked up by
    UID via the ``getSampleTypeUID`` FieldIndex on the sample
    catalog, already registered by the catalog setup step). This
    avoids touching every sample on each SampleType edit. The
    legacy ``getHazardous`` metadata column on the sample catalog
    is removed since the flag is now resolved exclusively via the
    SampleType brain.
    """
    logger.info("Adding hazard categories ...")
    sample_catalog = api.get_tool(SAMPLE_CATALOG)
    del_column(sample_catalog, "getHazardous")
    setup_catalog = api.get_tool(SETUP_CATALOG)
    add_column(setup_catalog, "getHazardCategories")
    add_column(setup_catalog, "getHazardous")
    sample_types = setup_catalog({"portal_type": "SampleType"})
    logger.info(
        "Refreshing metadata for %d SampleType(s) ...", len(sample_types))
    for brain in sample_types:
        obj = api.get_object(brain)
        # Metadata-only refresh: don't recompute every index.
        setup_catalog.catalog_object(
            obj, api.get_path(obj), idxs=[], update_metadata=1)
    logger.info("Adding hazard categories [DONE]")


@upgradestep(product, version)
def seed_detached_partition_backrefs(tool):
    """Seed annotation backrefs for already-detached partitions.

    The `DetachedFrom` field gained a `relationship` attribute so the
    UIDReferenceField now maintains backrefs on `setDetachedFrom`. Any
    detached partition created before this change has the forward UID
    pointer but no backref. Re-set the field to trigger backref
    maintenance on the link.
    """
    query = {
        "portal_type": "AnalysisRequest",
        "object_provides": IDetachedPartition.__identifier__,
    }
    brains = api.search(query, SAMPLE_CATALOG)
    total = len(brains)
    logger.info(
        "Seeding DetachedFrom backrefs for {} detached partitions".format(
            total))

    seeded = 0
    for num, brain in enumerate(brains, start=1):
        sample = api.get_object(brain)
        field = sample.getField("DetachedFrom")
        if field is None:
            continue
        target = field.get(sample)
        if target is None:
            continue
        # Re-setting via the field link API ensures the backref
        # annotation gets created on the target.
        field.link_reference(target, sample)
        seeded += 1
        if num % 100 == 0:
            logger.info("  ... seeded {}/{}".format(num, total))

    logger.info("Seeded DetachedFrom backrefs for {} samples".format(seeded))


@upgradestep(product, version)
def import_rolemap(tool):
    """Import rolemap step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    setup.runImportStepFromProfile(profile, "rolemap")


@upgradestep(product, version)
def setup_reattach_transition(tool):
    """Register the new 'reattach' workflow transition.

    Re-imports the sample workflow so existing instances pick up
    the 'reattach' transition (guarded by the existing
    "Detach Sample Partition" permission) and the matching
    exit-transitions on the live sample states.
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    setup.runImportStepFromProfile(profile, "workflow")


@upgradestep(product, version)
def setup_duplicate_sample_transition(tool):
    """Register the new 'duplicate_sample' workflow transition.

    Re-imports the workflow (new transition guarded by the
    existing AddAnalysisRequest permission, plus exit-transitions
    on existing states). Duplicates use the regular
    AnalysisRequest ID format, so no ID-server template needs to
    be installed.
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    setup.runImportStepFromProfile(profile, "workflow")


@upgradestep(product, version)
def remove_dashboard_registry_visibility(tool):
    """Remove legacy registry-based dashboard panel visibility

    The dashboard previously used a custom registry record
    'senaite.core.dashboard_panels_visibility' to store per-role
    visibility settings for each dashboard section. This was a
    hardcoded permission mapping that duplicated what Plone's
    standard role system already provides.

    The dashboard now uses a simple role check via DASHBOARD_ROLES
    instead of the registry. This step removes the stale registry
    record and re-imports the rolemap.
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    # Import rolemap
    setup.runImportStepFromProfile(profile, "rolemap")

    # Remove stale registry record
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility
    registry = getUtility(IRegistry)
    key = "senaite.core.dashboard_panels_visibility"
    if key in registry.records:
        del registry.records[key]
        logger.info("Removed registry record '%s'" % key)


@upgradestep(product, version)
def import_controlpanel(tool):
    """Import usersschema step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "controlpanel")


@upgradestep(product, version)
def import_registry(tool):
    """Import registry step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    # XXX: The plone.app.registry step depends on the typeinfo step, which
    # causes this error if executed w/o AT portal type removal first:
    #
    # Traceback (innermost last):
    #   Module ZPublisher.WSGIPublisher, line 176, in transaction_pubevents
    #   Module ZPublisher.WSGIPublisher, line 385, in publish_module
    #   Module ZPublisher.WSGIPublisher, line 288, in publish
    #   Module ZPublisher.mapply, line 85, in mapply
    #   Module ZPublisher.WSGIPublisher, line 63, in call_object
    #   Module Products.GenericSetup.tool, line 1135, in manage_doUpgrades
    #   Module Products.GenericSetup.upgrade, line 185, in doStep
    #   Module senaite.core.upgrade, line 39, in wrap_func_args
    #   Module senaite.core.upgrade.v02_07_000, line 86, in import_registry
    #   Module Products.GenericSetup.tool, line 375, in runImportStepFromProfile
    #   Module Products.GenericSetup.tool, line 1323, in _doRunImportStep
    #    - __traceback_info__: typeinfo
    #   Module Products.CMFCore.exportimport.typeinfo, line 222, in importTypesTool
    #   Module Products.GenericSetup.utils, line 934, in importObjects
    #    - __traceback_info__: portal_types
    #   Module Products.GenericSetup.utils, line 930, in importObjects
    #    - __traceback_info__: types/Contact
    #   Module Products.GenericSetup.utils, line 530, in _importBody
    #   Module Products.CMFCore.exportimport.typeinfo, line 61, in _importNode
    #   Module Products.GenericSetup.utils, line 763, in _initProperties
    # ValueError: undefined property 'add_permission'
    remove_at_portal_types(tool, REMOVE_AT_TYPES)

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
def migrate_calculations_to_dx(tool):
    """Converts existing calculations to Dexterity
    """
    logger.info("Convert Calculations to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool, REMOVE_AT_TYPES)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_calculations")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("calculations")

    # un-catalog the old container
    uncatalog_object(origin)

    # copy items from old -> new container
    objects = origin.objectValues()
    for num, src in enumerate(objects, start=1):
        migrate_calculation_to_dx(src, destination)
        if num % 100 == 0:
            transaction.savepoint()

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    remove_calculations_from_repositorytool()
    strip_calc_interims_from_services(tool)
    logger.info("Convert Calculations to Dexterity [DONE]")


def _delete_orphaned_reference(rc, ref):
    """Remove a Reference object whose source no longer exists.

    AT's _deleteReference returns early when getSourceObject() is None,
    leaving both the ZCatalog index entry and the Reference object itself
    in the ZODB. This function handles both:

    1. Uncatalogs the brain from rc._catalog so future getBackReferences
       calls do not find this entry.
    2. Deletes the Reference object from its annotation parent container
       to avoid leaving orphaned ZODB data.

    :param rc: The reference_catalog tool
    :param ref: The orphaned AT Reference object
    """
    try:
        path = "/".join(ref.getPhysicalPath())
        rc._catalog.uncatalog_object(path)
    except (AttributeError, KeyError, TypeError):
        pass
    try:
        parent = ref.aq_parent
        if parent is not None:
            parent._delObject(ref.id)
    except (AttributeError, KeyError, TypeError):
        pass


def migrate_calculation_to_dx(src, destination=None):
    """Migrate an AT profile to DX in the destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder of
                        the source object is taken
    """
    # migrate the contents from the old AT container to the new one
    portal_type = "Calculation"

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
    target.setPythonImports(src.getPythonImports() or [])
    target.setFormula(src.getFormula())
    target.setTestParameters(src.getTestParameters() or [])
    target.setTestResult(src.getTestResult() or "")
    target.setDependentServices(src.getDependentServices() or [])

    target_interims = []
    for src_interim in src.getInterimFields():
        interim = src_interim.copy()
        # ensure interim fields are unicode
        interim["unit"] = src_interim.get("unit") or ""
        interim["result_type"] = src_interim.get("result_type") or "numeric"
        interim["choices"] = src_interim.get("choices") or ""
        # AT uses 'wide'; DX IInterimField uses 'apply_wide'
        wide = interim.pop("wide", False)
        interim["apply_wide"] = bool(interim.pop("apply_wide", wide))
        # AT boolean subfields submitted via :records:ignore_empty are absent
        # when unchecked; normalise to explicit Python booleans so the DX
        # form renders them correctly.
        for key in ("allow_empty", "report", "hidden"):
            interim[key] = bool(src_interim.get(key, False))
        target_interims.append(interim)
    target.setInterimFields(target_interims)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # create backrefs storage for newly created calculation and
    # move there uids of AnalisysServiced dependendent on this calc
    key = "CalculationDependentServices"
    src_backreferences = get_backreferences(src, relationship=key)
    target_storage = get_backref_storage(target)
    target_backrefs = target_storage[key] = PersistentList()
    for ref in src_backreferences:
        target_backrefs.append(api.get_uid(ref))

    # NOTE: We need to create the correct snapshot versions based on the stored
    # versions of the repository tool
    # migrator.copy_snapshots(src, target)
    pr = api.get_tool("portal_repository")
    for record in pr.getHistory(src, oldestFirst=True):
        # get the calculation object
        obj = record.object
        # create a snapshot for this object
        snapshot = snap_api.take_snapshot(obj, store=False)
        snapshot["__metadata__"].update({
            "actor": obj.Creator() or "migrator",
            "modified": obj.modified().ISO(),
            "snapshot_created": obj.created().ISO(),
            "comments": "Migrated snapshot from AT version {0}".format(
                record.version_id),
        })
        # store the snapshot on the target object
        storage = snap_api.get_storage(target)
        # append the JSON snapshot to the storage
        storage.append(json.dumps(snapshot))

    # provide the IAuditable interface to the target object
    alsoProvides(target, IAuditable)

    # disable the IVersioned interface on the source object
    if IVersioned.providedBy(src):
        noLongerProvides(src, IVersioned)

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

    # Stamp the snapshotted calculation data onto every Analysis that
    # referenced this Calculation via the old AT reference_catalog entry.
    # We set each field directly to avoid triggering the new setCalculation
    # side-effects (interim merging) on already-initialized analyses and to
    # avoid any dependency on the old Calculation AT field still existing.
    rc = api.get_tool("reference_catalog")
    refs = rc.getBackReferences(src, relationship="AnalysisCalculation")
    calc_uid = api.get_uid(target)
    calc_formula = target.getMinifiedFormula()
    calc_imports = json.dumps(target.getPythonImports() or [])
    calc_version = api.get_version(target) or 0
    stale_refs = 0
    for ref in refs:
        analysis = ref.getSourceObject()
        if not analysis:
            # Source Analysis no longer exists (deleted without proper
            # reference cleanup). AT's _deleteReference bails out when
            # sobj is None, so uncatalog the brain directly to prevent
            # this stale entry from appearing in future catalog queries.
            stale_refs += 1
            logger.debug(
                "Stale AnalysisCalculation ref skipped: {}".format(ref))
            _delete_orphaned_reference(rc, ref)
            continue
        analysis.getField("CalculationUID").set(analysis, calc_uid)
        analysis.getField("CalculationFormula").set(analysis, calc_formula)
        analysis.getField("CalculationImports").set(analysis, calc_imports)
        analysis.getField("CalculationVersion").set(analysis, calc_version)
        analysis.deleteReferences(relationship="AnalysisCalculation")
    if stale_refs:
        logger.warn(
            "Removed {} stale AnalysisCalculation ref(s) for: {}".format(
                stale_refs, api.get_path(src)))

    logger.info("Migrated Calculation from %s -> %s" % (src, target))


def strip_calc_interims_from_services(tool):
    """Remove from each AnalysisService the interim fields that are already
    defined by its assigned calculation.

    After the AT->DX Calculation migration the system uses a clean separation:
    calculation interims and service interims are stored independently.
    When a sample analysis is created, calc interims come first and
    service-only interims are appended. Services must therefore not carry
    duplicates of the calc interims.
    """
    logger.info("Strip calculation interims from analysis services ...")
    brains = api.search(
        {"portal_type": "AnalysisService"}, SETUP_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info(
                "Processing services {}/{}".format(num, total))
            transaction.savepoint()
        service = api.get_object(brain)
        _strip_calc_interims(service)
        service._p_deactivate()
    logger.info(
        "Strip calculation interims from analysis services [DONE]")


def _strip_calc_interims(service):
    """Remove calc-sourced interims from a single service in-place."""
    calc = service.getCalculation()
    if not calc:
        return
    calc_keywords = {
        i.get("keyword") for i in calc.getInterimFields()
    }
    service_interims = service.getInterimFields()
    filtered = [
        i for i in service_interims
        if i.get("keyword") not in calc_keywords
    ]
    if len(filtered) == len(service_interims):
        return
    service.setInterimFields(filtered)
    logger.info(
        "Stripped {0} calc interim(s) from service '{1}'".format(
            len(service_interims) - len(filtered),
            api.get_title(service)))


def remove_calculations_from_repositorytool():
    """Remove Calculation from Repository Tool
    """
    logger.info("Remove auto versioning for Calculations ...")
    portal_type = "Calculation"

    rt = api.get_tool("portal_repository")
    mapping = rt._version_policy_mapping
    mapping.pop(portal_type, None)
    rt._version_policy_mapping = mapping
    versionable_types = rt.getVersionableContentTypes()
    if portal_type in versionable_types:
        versionable_types.remove(portal_type)
        rt.setVersionableContentTypes(versionable_types)

    logger.info("Remove auto versioning for Calculation... [DONE]")


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

        items = [PORTAL_FOLDER_ITEMS[folder_id]]
        add_dexterity_items(portal, items)
        folder = portal.get(folder_id)
    return folder


@upgradestep(product, version)
def migrate_contacts_to_dx(tool):
    """Migrate Contact objects from Archetypes to Dexterity
    """
    logger.info("Migrating Contacts to Dexterity ...")

    # Ensure old AT types are flushed first
    remove_at_portal_types(tool, REMOVE_AT_TYPES)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")

    # Find all Contact objects (excluding LabContact and SupplierContact)
    query = {
        "portal_type": "Contact",
    }
    brains = api.search(query, CONTACT_CATALOG)
    total = len(brains)
    logger.info("Found {} Contact objects to migrate".format(total))

    for num, brain in enumerate(brains, start=1):
        # Get the object
        contact = api.get_object(brain)

        if num % 100 == 0:
            logger.info("Progress: {}/{} contacts migrated".format(num, total))
            transaction.savepoint()

        # Skip if already migrated to Dexterity
        if not api.is_at_content(contact):
            logger.info("[{}/{}] Already migrated: {}".format(
                num, total, api.get_path(contact)))
            continue

        migrate_contact_to_dx(contact)

    logger.info("Migrating Contacts to Dexterity [DONE]")


def migrate_contact_to_dx(src, destination=None):
    """Migrate an AT contact to DX in the destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder of
                        the source object is taken
    """
    # migrate the contents from the old AT container to the new one
    portal_type = "Contact"

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
        # Don't use the api to skip the auto-id generation
        target = createContent(portal_type, id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = u""  # calculated
    target.description = u""  # not used
    target.salutation = api.safe_unicode(src.getSalutation() or "")
    target.firstname = api.safe_unicode(src.getFirstname() or "")
    target.middleinitial = api.safe_unicode(src.getMiddleinitial() or "")
    target.middlename = api.safe_unicode(src.getMiddlename() or "")
    target.surname = api.safe_unicode(src.getSurname() or "")
    target.username = api.safe_unicode(src.getUsername() or "")
    target.email_address = api.safe_unicode(src.getEmailAddress() or "")
    target.business_phone = api.safe_unicode(src.getBusinessPhone() or "")
    target.business_fax = api.safe_unicode(src.getBusinessFax() or "")
    target.home_phone = api.safe_unicode(src.getHomePhone() or "")
    target.mobile_phone = api.safe_unicode(src.getMobilePhone() or "")
    target.job_title = api.safe_unicode(src.getJobTitle() or "")
    target.department = api.safe_unicode(src.getDepartment() or "")
    target.cc_contact = src.getRawCCContact() or []

    # NOTE: Addresses behave differently in AT and DX
    physical_address = src.getPhysicalAddress() or {}
    if physical_address:
        address = to_dx_address(physical_address, PHYSICAL_ADDRESS)
        target.setPhysicalAddress(address)

    postal_address = src.getPostalAddress() or {}
    if postal_address:
        address = to_dx_address(postal_address, POSTAL_ADDRESS)
        target.setPostalAddress(address)

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

    # move eventual contents from source to target
    if api.is_folderish(src):
        cp = src.manage_cutObjects(ids=src.objectIds())
        target.manage_pasteObjects(cp)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    # Ensure user is correctly linked to the contact
    if target.getUsername():
        target.setUser(target.getUsername())

    logger.info("Migrated Contact from %s -> %s" % (src, target))


def migrate_multifiles_to_dx(tool):
    """Migrate Multifile objects from Archetypes to Dexterity
    """
    logger.info("Migrating Multifiles to Dexterity ...")

    # Ensure old AT types are flushed first
    remove_at_portal_types(tool, REMOVE_AT_TYPES)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")

    # Find all Multifile objects
    query = {
        "portal_type": "Multifile",
    }
    brains = api.search(query, SETUP_CATALOG)
    total = len(brains)
    logger.info("Found {} Multifile objects to migrate".format(total))

    for num, brain in enumerate(brains, start=1):
        # Get the object
        multifile = api.get_object(brain)

        if num % 100 == 0:
            logger.info("Progress: {}/{} multifiles migrated".format(num, total))
            transaction.savepoint()

        # Skip if already migrated to Dexterity
        if not api.is_at_content(multifile):
            logger.info("[{}/{}] Already migrated: {}".format(
                num, total, api.get_path(multifile)))
            continue

        migrate_multifile_to_dx(multifile)

    logger.info("Migrating Multifiles to Dexterity [DONE]")


@upgradestep(product, version)
def migrate_multifile_to_dx(src, destination=None):
    """Migrate an AT multifile to DX in the destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder of
                        the source object is taken
    """
    # migrate the contents from the old AT container to the new one
    portal_type = "Multifile"

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
        # Don't use the api to skip the auto-id generation
        target = createContent(portal_type, id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = u""  # calculated from document_id
    target.description = u""  # not used
    target.document_id = u(src.getDocumentID())
    target.document_version = u(src.getDocumentVersion())
    target.document_location = u(src.getDocumentLocation())
    target.document_type = u(src.getDocumentType())

    # Handle file field - convert AT BlobWrapper to DX NamedBlobFile
    file_field = src.getField("File")
    if file_field:
        file_data = file_field.get(src)
        if file_data:
            # Convert BlobWrapper to NamedBlobFile
            if isinstance(file_data, BlobWrapper):
                filename = file_data.getFilename()
                content_type = file_data.getContentType()
                data = file_data.data
                target.file = NamedBlobFile(
                    data=data,
                    filename=u(filename),
                    contentType=content_type
                )
            else:
                # Fallback for other types
                target.file = file_data

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

    # move eventual contents from source to target
    if api.is_folderish(src):
        cp = src.manage_cutObjects(ids=src.objectIds())
        target.manage_pasteObjects(cp)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    logger.info("Migrated Multifile from %s -> %s" % (src, target))


def migrate_laboratory_to_dx(tool):
    """Migrates Laboratory to DX
    """
    logger.info("Convert Laboratory to Dexterity ...")

    remove_at_portal_types(tool, REMOVE_AT_TYPES)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")

    portal_type = "Laboratory"
    query = {
        "portal_type": portal_type,
    }
    brains = api.search(query, SETUP_CATALOG)

    if not brains:
        logger.warning("No Laboratory object found, skipping migration")
        return

    src = api.get_object(brains[0])

    # Check if already migrated
    if not api.is_at_content(src):
        logger.info(
            "Laboratory already migrated: {}".format(api.get_path(src)))
        return

    destination = api.get_senaite_setup()
    migrate_at_laboratory_to_dx(src, destination)

    logger.info("Convert Laboratory to Dexterity [DONE]")


def migrate_at_laboratory_to_dx(src, destination):
    """Create a DX Laboratory in `destination` from the AT `src`, copy all
    data over, remove the AT source and adopt its id. Returns the new DX
    Laboratory object.
    """
    portal_type = "Laboratory"
    src_id = api.get_id(src)
    target_id = tmpID()

    target = destination.get(src_id)
    if not target:
        # Don't use the api to skip the auto-id generation
        target = createContent(portal_type, id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = u(src.getName() or "")
    target.description = u(src.Description() or "")

    # Laboratory-specific fields
    target.lab_url = u(src.getLabURL() or "")
    target.supervisor = src.getRawSupervisor() or ""
    target.confidence = src.getConfidence() or None
    target.laboratory_accredited = bool(src.getLaboratoryAccredited())
    target.accreditation_body = u(src.getAccreditationBody() or "")
    target.accreditation_body_url = u(src.getAccreditationBodyURL() or "")
    target.accreditation = u(src.getAccreditation() or "")
    target.accreditation_reference = u(src.getAccreditationReference() or "")
    target.accreditation_body_logo = blob_to_named_file(
        src.getAccreditationBodyLogo(), default_filename=u"logo.png")
    target.accreditation_page_header = u(src.getAccreditationPageHeader() or "")

    # Organization fields (inherited from Organisation)
    target.tax_number = u(src.getTaxNumber() or "")
    target.phone = u(src.getPhone() or "")
    target.fax = u(src.getFax() or "")
    target.email = u(src.getEmailAddress() or "")
    target.account_type = u(src.getAccountType() or "")
    target.account_name = u(src.getAccountName() or "")
    target.account_number = u(src.getAccountNumber() or "")
    target.bank_name = u(src.getBankName() or "")
    target.bank_branch = u(src.getBankBranch() or "")

    # Copy addresses using the to_dx_address helper
    postal_address = src.getPostalAddress() or {}
    if postal_address:
        target.setPostalAddress(
            to_dx_address(postal_address, POSTAL_ADDRESS)
        )

    physical_address = src.getPhysicalAddress() or {}
    if physical_address:
        target.setPhysicalAddress(
            to_dx_address(physical_address, PHYSICAL_ADDRESS)
        )

    billing_address = src.getBillingAddress() or {}
    if billing_address:
        target.setBillingAddress(
            to_dx_address(billing_address, BILLING_ADDRESS)
        )

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

    # Ensure Laboratory is allowed in its container before rename
    permanently_allow_type_for(api.get_portal_type(destination), portal_type)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    target.reindexObject()

    logger.info("Migrated Laboratory from %s -> %s" % (src, target))
    return target


def get_laboratory_objects(containers):
    """Return all Laboratory objects contained in the given containers
    """
    laboratories = []
    for container in containers:
        if container is None:
            continue
        for object_id in list(container.objectIds()):
            obj = container._getOb(object_id, None)
            if obj is None:
                continue
            if api.get_portal_type(obj) == "Laboratory":
                laboratories.append(obj)
    return laboratories


def pick_primary_laboratory(setup, bika_setup):
    """Pick the Laboratory that holds the live data

    The former `SenaiteSetup.laboratory` property returned
    `bika_setup.laboratory`, so any data entered through the UI lives
    there. Fall back to the setup folder otherwise.
    """
    candidates = []
    if bika_setup is not None and "laboratory" in bika_setup.objectIds():
        candidates.append(bika_setup._getOb("laboratory"))
    if "laboratory" in setup.objectIds():
        candidates.append(setup._getOb("laboratory"))
    if "laboratory-1" in setup.objectIds():
        candidates.append(setup._getOb("laboratory-1"))
    # any other Laboratory as last resort
    candidates.extend(get_laboratory_objects([setup, bika_setup]))
    return candidates[0] if candidates else None


def consolidate_laboratory(tool):
    """Consolidate duplicate Laboratory objects into a single
    `setup/laboratory`

    The Laboratory was only half-moved into the DX `setup` folder: the
    bika.lims structure profile still created `bika_setup/laboratory`
    and `add_dexterity_setup_items` produced an empty `setup/laboratory-1`
    (the `laboratory` id was blocked by the former
    `SenaiteSetup.laboratory` property). This keeps the single
    data-bearing Laboratory, migrates it to DX inside `setup` if needed,
    removes the duplicates and ensures the canonical id `laboratory`.
    """
    logger.info("Consolidate Laboratory ...")

    setup = api.get_senaite_setup()
    bika_setup = api.get_bika_setup()

    primary = pick_primary_laboratory(setup, bika_setup)
    if primary is None:
        logger.warning("No Laboratory object found, nothing to consolidate")
        return

    primary_uid = api.get_uid(primary)

    # Remove every other Laboratory so the `laboratory` id becomes free
    for lab in get_laboratory_objects([setup, bika_setup]):
        if api.get_uid(lab) == primary_uid:
            continue
        logger.info("Removing duplicate Laboratory: %s" % api.get_path(lab))
        api.delete(lab, check_permissions=False)

    # Ensure the type is allowed in the setup folder
    permanently_allow_type_for(api.get_portal_type(setup), "Laboratory")

    # Ensure the primary is a DX object living in the setup folder
    if api.is_at_content(primary):
        primary = migrate_at_laboratory_to_dx(primary, setup)
    elif api.get_path(api.get_parent(primary)) != api.get_path(setup):
        primary = api.move_object(primary, setup, check_constraints=False)

    # Ensure the canonical id is `laboratory`
    if api.get_id(primary) != "laboratory":
        parent = api.get_parent(primary)
        parent.manage_renameObject(api.get_id(primary), "laboratory")
        primary = parent._getOb("laboratory")

    primary.reindexObject()
    logger.info("Consolidate Laboratory [DONE]: %s" % api.get_path(primary))


LABORATORY_IMAGE_FIELDS = (
    ("accreditation_body_logo", u"logo.png"),
)


@upgradestep(product, version)
def repair_laboratory_migration(tool):
    """Repair the Laboratory-to-DX migration

    Two issues need patching on already-migrated instances:

    1. Before #2902, the migration passed AT ImageField values straight
       through `blob_to_named_file` when they were not BlobWrapper
       instances. The raw `OFS.Image.Image` objects were assigned to
       the new `NamedBlobImage` field, which is neither None nor
       INamed; `plone.formwidget.namedfile` then crashes rendering
       the laboratory view or edit form.

    2. The new Laboratory FTI was missing the
       `IMultiCatalogBehavior` behavior, so the catalog multiplex
       processor refused to index it in any non-portal catalog. The
       result is that the laboratory is absent from
       `senaite_catalog_setup` and any code that resolves it through
       catalog (e.g. `SuperModel` lookups in impress) gets nothing.
    """
    logger.info("Repair laboratory migration ...")

    # Re-import typeinfo so the FTI picks up IMultiCatalogBehavior
    tool.runImportStepFromProfile(profile, "typeinfo")

    setup = api.get_senaite_setup()
    laboratory = setup.get("laboratory") if setup else None
    if laboratory is None:
        logger.info("No laboratory found, skipping repair")
        return

    # Re-wrap legacy OFS.Image values on the named-file fields
    for fieldname, default_filename in LABORATORY_IMAGE_FIELDS:
        repair_laboratory_image_field(
            laboratory, fieldname, default_filename)

    # Reindex so the multiplex processor now lands the laboratory in
    # senaite_catalog_setup (and the other catalogs mapped to it)
    laboratory.reindexObject()
    logger.info("Reindexed %s" % laboratory)

    logger.info("Repair laboratory migration [DONE]")


def repair_laboratory_image_field(laboratory, fieldname, default_filename):
    """Re-wrap a single image field if it holds a non-INamed legacy value
    """
    value = getattr(laboratory, fieldname, None)
    if value is None:
        return
    if INamed.providedBy(value):
        return
    named = blob_to_named_file(value, default_filename=default_filename)
    setattr(laboratory, fieldname, named)
    logger.info("Repaired %s.%s (%s -> %s)" % (
        laboratory, fieldname, type(value).__name__,
        type(named).__name__ if named is not None else None))


def to_dx_address(value, address_type=NAIVE_ADDRESS):
    return {
        "type": u(value.get("address_type") or address_type),
        "address": u(value.get("address") or ""),
        "zip": u(value.get("zip") or ""),
        "city": u(value.get("city") or ""),
        "subdivision1": u(value.get("state") or ""),
        "subdivision2": u(value.get("district") or ""),
        "country": u(value.get("country") or ""),
    }


@upgradestep(product, version)
def create_setup_contacts_folder(tool):
    """Create the Contacts container in the setup folder
    """
    logger.info("Creating Contacts container in setup folder ...")

    # Ensure old AT types are flushed first
    remove_at_portal_types(tool, REMOVE_AT_TYPES)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "actions")

    setup = api.get_senaite_setup()

    # Check if contacts folder already exists
    if not setup.get("contacts"):
        items = [("contacts", "Contacts", "Contacts")]
        add_dexterity_items(setup, items)
        logger.info("Contacts container created")
    else:
        logger.info("Contacts folder already exists [SKIP]")

    logger.info("Creating Contacts container in setup folder [DONE]")


@upgradestep(product, version)
def notify_upgrade(context):
    """Dummy func to force the call of before and after upgrade events
    """
    pass


@upgradestep(product, version)
def setup_custom_image_and_file_types(tool):
    """Setup custom File and Image types and add Attachments catalog
    """
    logger.info("Setup custom File and Image types ...")
    # Ensure old AT types are flushed first
    remove_at_portal_types(tool, REMOVE_AT_TYPES)
    portal = tool.aq_inner.aq_parent
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")
    # Needed for the updated Client.xml action
    _run_import_step(portal, "typeinfo", "profile-bika.lims:default")
    setup_core_catalogs(portal)
    logger.info("Setup custom File and Image types [DONE]")


@upgradestep(product, version)
def link_contact_users(tool):
    """This upgrade step ensures that the client contacts are linked correctly
    to their users
    """
    logger.info("Link client contacts to users ...")
    query = {"portal_type": "Contact"}
    brains = api.search(query, CONTACT_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Linking contacts to users {0}/{1}"
                        .format(num, total))
            transaction.savepoint()

        contact = api.get_object(brain)
        username = contact.getUsername()
        if not username:
            continue
        contact.setUser(username)
        logger.info("Linking user '{}' -> Contact '{}'"
                    .format(username, api.get_path(contact)))
        contact._p_deactivate()

    logger.info("Link client contacts to users [DONE]")


@upgradestep(product, version)
def migrate_setup_fields_to_dx(tool):
    """Migrate all setup fields from BikaSetup to SenaiteSetup
    """
    logger.info("Migrating setup fields from BikaSetup to SenaiteSetup ...")

    bika_setup = api.get_bika_setup()
    senaite_setup = api.get_senaite_setup()

    if not bika_setup or not senaite_setup:
        logger.warning("BikaSetup or SenaiteSetup not found [SKIP]")
        return

    # Mapping of AT field name -> DX field name
    # Format: (AT_field_name, DX_field_name, converter_function)
    fields_to_migrate = (
        # Security
        ("AutoLogOff", "auto_log_off", None),
        ("RestrictWorksheetUsersAccess", "restrict_worksheet_users_access",
         None),
        ("AllowToSubmitNotAssigned", "allow_to_submit_not_assigned", None),
        ("RestrictWorksheetManagement", "restrict_worksheet_management", None),
        ("EnableGlobalAuditlog", "enable_global_auditlog", None),
        # Accounting
        ("ShowPrices", "show_prices", None),
        ("Currency", "currency", None),
        ("DefaultCountry", "default_country", None),
        ("MemberDiscount", "member_discount", None),
        ("VAT", "vat", None),
        # Results Reports
        ("DecimalMark", "decimal_mark", None),
        ("ScientificNotationReport", "scientific_notation_report", None),
        ("MinimumResults", "minimum_results", None),
        # Analyses
        ("CategoriseAnalysisServices", "categorise_analysis_services", None),
        ("CategorizeSampleAnalyses", "categorize_sample_analyses", None),
        ("SampleAnalysesRequired", "sample_analyses_required", None),
        ("AllowManualResultCaptureDate", "allow_manual_result_capture_date",
         None),
        ("EnableARSpecs", "enable_ar_specs", None),
        ("ExponentialFormatThreshold", "exponential_format_threshold", None),
        ("ImmediateResultsEntry", "immediate_results_entry", None),
        ("EnableAnalysisRemarks", "enable_analysis_remarks", None),
        ("AutoVerifySamples", "auto_verify_samples", None),
        ("SelfVerificationEnabled", "self_verification_enabled", None),
        ("NumberOfRequiredVerifications", "number_of_required_verifications",
         None),
        ("TypeOfmultiVerification", "type_of_multi_verification", None),
        ("ResultsDecimalMark", "results_decimal_mark", None),
        ("ScientificNotationResults", "scientific_notation_results", None),
        ("RejectionReasons", "rejection_reasons", "rejection_reasons"),
        ("DefaultNumberOfARsToAdd", "default_number_of_ars_to_add", None),
        ("MaxNumberOfSamplesAdd", "max_number_of_samples_add", None),
        # Appearance
        ("WorksheetLayout", "worksheet_layout", None),
        ("DashboardByDefault", "dashboard_by_default", None),
        ("LandingPage", "landing_page", None),
        ("ShowPartitions", "show_partitions", None),
        ("ShowLabNameInLogin", "show_lab_name_in_login", None),
        # Sampling
        ("PrintingWorkflowEnabled", "printing_workflow_enabled", None),
        ("SamplingWorkflowEnabled", "sampling_workflow_enabled", None),
        ("ScheduleSamplingEnabled", "schedule_sampling_enabled", None),
        ("DateSampledRequired", "date_sampled_required", None),
        ("AutoreceiveSamples", "autoreceive_samples", None),
        ("SamplePreservationEnabled", "sample_preservation_enabled", None),
        ("Workdays", "workdays", None),
        ("DefaultTurnaroundTime", "default_turnaround_time", "duration"),
        ("DefaultSampleLifetime", "default_sample_lifetime", "duration"),
        # Notifications
        ("EmailFromSamplePublication", "email_from_sample_publication", None),
        ("EmailBodySamplePublication", "email_body_sample_publication", None),
        ("AlwaysCCResponsiblesInReportEmail",
         "always_cc_responsibles_in_report_emails", None),
        ("NotifyOnSampleRejection", "notify_on_sample_rejection", None),
        ("EmailBodySampleRejection", "email_body_sample_rejection", None),
        ("InvalidationReasonRequired", "invalidation_reason_required", None),
        ("EmailBodySampleInvalidation", "email_body_sample_invalidation",
         None),
        # Sticker
        ("AutoPrintStickers", "auto_print_stickers", None),
        ("AutoStickerTemplate", "auto_sticker_template", None),
        ("SmallStickerTemplate", "small_sticker_template", None),
        ("LargeStickerTemplate", "large_sticker_template", None),
        ("DefaultNumberOfCopies", "default_number_of_copies", None),
        # ID Server
        ("IDFormatting", "id_formatting", None),
    )

    migrated = 0
    skipped = 0
    errors = 0

    for field_info in fields_to_migrate:
        at_field_name = field_info[0]
        dx_field_name = field_info[1]
        converter = field_info[2] if len(field_info) > 2 else None

        # Get the AT field
        at_field = bika_setup.getField(at_field_name)
        if not at_field:
            logger.warning("AT field {} not found [SKIP]".format(
                at_field_name))
            skipped += 1
            continue

        # Get raw value from AT field
        try:
            raw_value = at_field.get(bika_setup)
        except Exception as e:
            logger.error("Error reading AT field {}: {} [SKIP]".format(
                at_field_name, str(e)))
            errors += 1
            continue

        # we use the same setter names as in the AT setup
        setter_name = "set{}".format(at_field_name)

        # Check if setter exists on SenaiteSetup
        setter = getattr(senaite_setup, setter_name, None)
        if not setter or not callable(setter):
            logger.warning("Setter {} not found on SenaiteSetup [SKIP]".format(
                setter_name))
            skipped += 1
            continue

        try:
            # Apply converter if specified
            converted_value = raw_value
            if converter == "duration":
                # Convert dict to timedelta
                if isinstance(raw_value, dict):
                    converted_value = dtime.to_timedelta(raw_value)
                elif not isinstance(raw_value, timedelta):
                    logger.warning(
                        "Expected dict or timedelta for {}, got {} [SKIP]".format(
                            at_field_name, type(raw_value)))
                    skipped += 1
                    continue
            elif converter == "rejection_reasons":
                # Special handling for RejectionReasons
                # Extract checkbox and reasons from RecordsField
                if raw_value and isinstance(raw_value, (list, tuple)):
                    if len(raw_value) > 0 and isinstance(raw_value[0], dict):
                        reasons_dict = raw_value[0]
                        # Set enable_rejection_workflow based on checkbox
                        checkbox = reasons_dict.get("checkbox", "")
                        senaite_setup.setEnableRejectionWorkflow(
                            checkbox == "on")
                        # Extract textfield-* values
                        textfield_keys = [k for k in reasons_dict.keys()
                                          if k.startswith("textfield-")]
                        sorted_keys = sorted(
                            textfield_keys,
                            key=lambda x: int(x.split("-")[1]))
                        converted_value = [
                            api.safe_unicode(reasons_dict[k])
                            for k in sorted_keys
                            if reasons_dict[k]
                        ]
                    else:
                        converted_value = []
                else:
                    converted_value = []

            # Set value on SenaiteSetup
            setter(converted_value)

            logger.info("Migrated {} -> {}: {}".format(
                at_field_name, dx_field_name, repr(converted_value)))
            migrated += 1

        except Exception as e:
            logger.error("Error migrating {} -> {}: {}".format(
                at_field_name, dx_field_name, str(e)))
            errors += 1

    logger.info("Migration summary: {} migrated, {} skipped, {} errors".format(
        migrated, skipped, errors))

    logger.info("Migrating setup fields [DONE]")


@upgradestep(product, version)
def migrate_arreport_to_resultsreport(tool):
    """Migrate ARReport from Archetypes to Dexterity ResultsReport
    """
    logger.info("Migrating ARReport to Dexterity ResultsReport ...")

    # Remove AT portal type and install DX portal type
    remove_at_portal_types(tool, REMOVE_AT_TYPES)
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # Update AnalysisRequest to allow ResultsReport as subobject
    permanently_allow_type_for("AnalysisRequest", "ResultsReport")

    # Find all ARReport objects
    catalog = api.get_tool(REPORT_CATALOG)
    query = {"portal_type": "ARReport"}
    brains = catalog(query)
    total = len(brains)
    logger.info("Found {} ARReport objects to migrate".format(total))

    for num, brain in enumerate(brains, start=1):
        # Get the object
        arreport = api.get_object(brain)

        if num % 1000 == 0:
            logger.info("Progress: {}/{} reports migrated".format(num, total))
            # NOTE: We do a full transaction commit to avoid the following
            # error during this upgrade:
            #
            # Traceback (innermost last):
            #   [...]
            #   Module ZEO.TransactionBuffer, line 56, in store
            # IOError: [Errno 28] No space left on device
            transaction.commit()

        # Skip if already migrated to Dexterity
        if not api.is_at_content(arreport):
            logger.info("[{}/{}] Already migrated: {}".format(
                num, total, api.get_path(arreport)))
            continue

        try:
            migrate_arreport_to_dx(arreport)
        except Exception as e:
            logger.error("Error migrating {}: {}".format(
                api.get_path(arreport), str(e)))
            continue

    logger.info("Migrating ARReport to Dexterity ResultsReport [DONE]")


def migrate_arreport_to_dx(src, destination=None):
    """Migrate an AT ARReport to DX ResultsReport in the destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder
                        of the source object is taken
    """

    # migrate the contents from the old AT container to the new one
    old_portal_type = "ARReport"
    new_portal_type = "ResultsReport"

    if api.get_portal_type(src) != old_portal_type:
        logger.error("Not an '{}' object: {}".format(old_portal_type, src))
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
        # Don't use the api to skip the auto-id generation
        target = createContent(new_portal_type, id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!

    # Get Metadata (RecordField -> Dict)
    metadata = src.getMetadata()
    if metadata:
        # Store as plain dict
        target.metadata = metadata if isinstance(metadata, dict) else {}

    # Get SendLog (RecordsField -> DataGridField)
    sendlog = src.getSendLog()
    if sendlog:
        # Convert datetime fields to Python datetime (naive)
        sendlog_list = sendlog if isinstance(sendlog, list) else []
        for record in sendlog_list:
            if "email_send_date" in record and record["email_send_date"]:
                email_send_date = record.get("email_send_date")
                if email_send_date:
                    dt = dtime.to_dt(email_send_date)
                    record["email_send_date"] = dt
        target.send_log = sendlog_list

    # XXX: We removed the raw HTML field entirely from the DX content!
    # https://github.com/senaite/senaite.core/pull/2831#discussion_r2684057824
    # html = src.getHtml()

    # Get PDF file
    pdf_data = src.getPdf()
    if pdf_data:
        if isinstance(pdf_data, BlobWrapper):
            filename = pdf_data.getFilename() or "report.pdf"
            content_type = pdf_data.getContentType()
            data = pdf_data.data
            target.pdf = NamedBlobFile(
                data=data,
                filename=u(filename),
                contentType=content_type
            )

    # Get Recipients (RecordsField -> DataGridField)
    recipients = src.getRecipients()
    if recipients:
        target.recipients = recipients if isinstance(
            recipients, list) else []

    # Get DatePrinted
    date_printed = src.getDatePrinted()
    if date_printed:
        target.date_printed = dtime.to_dt(date_printed)

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

    # move eventual contents from source to target
    if api.is_folderish(src):
        if src.objectIds():
            cp = src.manage_cutObjects(ids=src.objectIds())
            target.manage_pasteObjects(cp)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    # IMPORTANT:
    #
    # We set these values *after* the UID was copied to ensure that the
    # backreferences are correctly created on the sample!

    # Get the primary analysis request and migrate its backreference
    sample = src.getAnalysisRequest()

    if sample:
        target.setSample(api.get_uid(sample))

    # Get contained analysis requests and migrate their backreferences
    contained_samples = src.getContainedAnalysisRequests()
    if contained_samples:
        uids = [api.get_uid(ref) for ref in contained_samples if ref]
        target.setContainedSamples(uids)

    # Reindex the object
    target.reindexObject()

    logger.info("Migrated ARReport from %s -> %s" % (src, target))


@upgradestep(product, version)
def migrate_worksheets_to_dx(tool):
    """Convert existing worksheet templates to Dexterity
    """
    logger.info("Convert Worksheet's to Dexterity ...")

    # Delete rejected analysis and empty worksheets
    # before install new content type
    cleanup_rejected_worksheets()

    # get the current allowed types for portal
    portal = api.get_portal()
    pt = api.get_tool("portal_types")
    type_info = pt.getTypeInfo(portal)
    allowed_types = type_info.allowed_content_types

    # in case the upgrade step fails with partial migrated contents
    origin = portal.get("worksheets-old", None)

    # check if WS folder is AT
    ws_container = portal.get("worksheets", None)
    if ws_container is not None and api.is_at_content(ws_container):
        # temporarily append WorksheetFolder as an allowed type
        portal_type = "WorksheetFolder"
        if portal_type not in type_info.allowed_content_types:
            type_info.allowed_content_types = allowed_types + (portal_type,)

        # Rename old AT worksheets folder
        portal.manage_renameObject("worksheets", "worksheets-old")

        # restore the allowed_types
        type_info.allowed_content_types = allowed_types

        origin = portal.get("worksheets-old")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool, REMOVE_AT_TYPES)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")
    tool.runImportStepFromProfile(profile, "rolemap")
    tool.runImportStepFromProfile(profile, "plone.app.registry")

    # get the destination container
    new_dx_folder = get_destination_folder("worksheets")

    # un-catalog the old container
    if origin:
        uncatalog_object(origin)

    # Find all AT Worksheet objects
    query = {"portal_type": "Worksheet"}
    brains = api.search(query, WORKSHEET_CATALOG)
    total = len(brains)
    logger.info("Found {} Worksheet objects to migrate".format(total))

    catalog = api.get_tool(WORKSHEET_CATALOG)
    problematic = []
    for num, brain in enumerate(brains, start=1):
        if num % 1000 == 0:
            logger.info(
                "Progress: {}/{} worksheets migrated".format(num, total))
            transaction.commit()
        brain_path = brain.getPath()
        try:
            worksheet = api.get_object(brain)
        except (AttributeError, KeyError) as exc:
            logger.warn(
                "Cannot get Worksheet at %s: %s" % (brain_path, exc))
            catalog.uncatalog_object(brain_path)
            problematic.append(brain_path)
            continue
        migrate_worksheet_to_dx(worksheet, new_dx_folder)

    # remove old AT folder
    if origin and len(origin) == 0:
        portal.manage_delObjects(["worksheets-old"])

    if problematic:
        logger.warn(
            "Migration finished with {} skipped Worksheet(s):".format(
                len(problematic)))
        for path in problematic:
            logger.warn("  Stale brain removed, AT WS at: %s" % path)

    logger.info("Convert Worksheet's to Dexterity [DONE]")


def cleanup_rejected_worksheets():
    """Delete all rejected worksheets and RejectAnalysis
    """
    logger.info("Cleanup rejected worksheets...")

    rejected_analysis_query = {"portal_type": "RejectAnalysis"}
    for num, brain in enumerate(
            api.search(rejected_analysis_query, ANALYSIS_CATALOG)):
        if num and num % 100 == 0:
            transaction.savepoint()
        rejected_analysis = api.get_object(brain)
        api.delete(rejected_analysis, False)
        logger.info("Delete rejected analysis {}".format(rejected_analysis))

    rejected_worksheets = {
        "portal_type": "Worksheet",
        "review_state": "rejected",
    }
    for num, brain in enumerate(
            api.search(rejected_worksheets, WORKSHEET_CATALOG)):
        if num and num % 100 == 0:
            transaction.savepoint()
        ws = api.get_object(brain)
        if ws.objectValues():
            continue
        api.delete(ws, False)
        logger.info("Delete rejected worksheet {}".format(ws))

    logger.info("Cleanup rejected worksheets [DONE]")


def migrate_worksheet_to_dx(src, destination):
    """Migrate a Worksheet to DX in destination folder

    :param src: The source AT object
    :param destination: The destination folder
    """
    if not api.is_at_content(src):
        api.move_object(src, destination, check_constraints=False)
        logger.info("Already migrated: {}".format(api.get_path(src)))
        return

    target_id = tmpID()

    target = destination.get(target_id)
    if not target:
        # Don't use the api to skip the auto-id generation
        target = createContent("Worksheet", id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = u(src.Title() or "")
    target.description = u(src.Description() or "")
    target.worksheet_template = src.getRawWorksheetTemplate()
    target.method = src.getRawMethod()
    target.analyst = src.getAnalyst()
    target.instrument = src.getRawInstrument()
    target.results_layout = src.getResultsLayout()
    target.analyses = src.getAnalysesUIDs()

    # move layout
    layout = []
    for slot in src.getLayout():
        layout.append({
            "position": int(slot["position"]),
            "type": slot["type"],
            "container_uid": slot["container_uid"],
            "analysis_uid": slot["analysis_uid"],
        })
    target.layout_view = layout

    # move remarks
    remarks = []
    for remark_record in src.getRemarks():
        remarks.append({
            "id": remark_record.id,
            "user_id": remark_record.user_id,
            "user_name": remark_record.user_name,
            "created": dtime.to_dt(remark_record.created),
            "content": remark_record.content,
        })
    target.remarks = remarks

    # create backrefs storage for newly created Worksheet and
    # move there uids of Analyses dependendent on this worksheet
    key = "WorksheetAnalysis"
    for an in target.getAnalyses():
        old_an_backrefs = get_backreferences(an, relationship=key)
        an_new_storage = get_backref_storage(an)
        new_an_backrefs = an_new_storage[key] = PersistentList()
        for ref in old_an_backrefs:
            new_an_backrefs.append(api.get_uid(ref))

    # move Duplicate, Reject and Attachment to new worksheet
    for obj in src.objectValues():
        api.move_object(obj, target, False)

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


@upgradestep(product, version)
def migrate_analysis_columns_to_setup(tool):
    """Migrate analysis columns order from registry to setup
    """
    logger.info(
        "Migrating analysis columns order to setup ..."
    )
    from senaite.core.registry import get_registry_record
    from senaite.core.vocabularies.setup import ANALYSIS_COLUMNS
    from senaite.core.vocabularies.setup import WORKSHEET_ANALYSIS_COLUMNS

    setup = api.get_senaite_setup()

    # Migrate sample view columns
    registry_sample = get_registry_record(
        "sampleview_analysis_columns_order", default=[]
    ) or []
    if registry_sample:
        all_keys = list(ANALYSIS_COLUMNS.keys())
        # append missing columns in their default order
        missing = [
            k for k in all_keys if k not in registry_sample
        ]
        migrated = tuple(registry_sample) + tuple(missing)
        setup.setSampleviewAnalysisColumnsOrder(migrated)
        logger.info(
            "Migrated sample view columns: %s" % list(migrated)
        )

    # Migrate worksheet view columns
    registry_ws = get_registry_record(
        "worksheetview_analysis_columns_order", default=[]
    ) or []
    if registry_ws:
        all_keys = list(WORKSHEET_ANALYSIS_COLUMNS.keys())
        # append missing columns in their default order
        missing = [
            k for k in all_keys if k not in registry_ws
        ]
        migrated = tuple(registry_ws) + tuple(missing)
        setup.setWorksheetviewAnalysisColumnsOrder(migrated)
        logger.info(
            "Migrated worksheet view columns: %s"
            % list(migrated)
        )

    logger.info(
        "Migrating analysis columns order to setup [DONE]"
    )


@upgradestep(product, version)
def reindex_labcontact_searchable_text(tool):
    """Reindex contact catalog indexes for LabContact and SupplierContact

    The listing_searchable_text, sortable_title and getParentUID adapters
    were only registered for the new DX Contact type
    (senaite.core.interfaces.IContact), causing the indexes to store no
    data for the legacy AT LabContact and SupplierContact types. Explicit
    ZCML registrations were added for bika.lims.interfaces.ILabContact and
    bika.lims.interfaces.ISupplierContact. This step reindexes the affected
    indexes so existing objects are correctly indexed.
    """
    indexes = [
        "listing_searchable_text",
        "sortable_title",
        "getParentUID",
    ]
    for index in indexes:
        logger.info(
            "Reindexing %s in contact catalog ..." % index
        )
        reindex_index(CONTACT_CATALOG, index)
        logger.info(
            "Reindexing %s in contact catalog [DONE]" % index
        )


@upgradestep(product, version)
def rebuild_title_indexes(tool):
    """Clear and rebuild the title FieldIndex on every SENAITE catalog

    #2901 reindexed the title index across all base catalogs so a new
    generic indexer could populate them with unicode keys. The reindex
    rewrites entries per docid but does not clear the BTree first, so
    pre-existing byte-string keys for non-ASCII titles remain. Any
    subsequent insert of a unicode key (e.g. when creating or editing
    a DX object whose title contains non-ASCII characters) then raises
    `UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3` on
    BTree key comparison.

    Clearing the index before reindexing wipes all stale byte-string
    keys and lets the (post-#2901) indexer repopulate the BTree with
    a single unicode key type. Catalogs are discovered dynamically by
    walking the portal and filtering on `ISenaiteCatalogObject`, so
    custom catalogs registered by downstream add-ons are also covered.
    """
    logger.info("Rebuild title indexes ...")
    catalogs = list(iter_senaite_catalogs())
    total = len(catalogs)
    for num, catalog in enumerate(catalogs, start=1):
        logger.info(
            "Rebuilding title index on %s (%s/%s) ..." % (
                catalog.id, num, total))
        rebuild_index(catalog, "title")
    logger.info("Rebuild title indexes [DONE]")


@upgradestep(product, version)
def cleanup_sample_catalog(tool):
    """Clean up senaite_catalog_sample indexes and metadata columns

    - Remove obsolete FieldIndexes getProvince and getDistrict from the
      sample catalog. Client geography belongs on the client catalog and
      is not meaningful as a sample catalog index; reindexing is also
      not triggered when client address fields change.
    - Remove stale metadata columns from the sample catalog: getProvince,
      getDistrict, getClientURL, getTemplateURL, getPhysicalPath. URLs
      are fragile (hostname-dependent) and better resolved at render
      time via memoized UID lookups. getPhysicalPath is unused.
    """
    logger.info("Cleaning up sample catalog indexes and columns ...")

    catalog = api.get_tool(SAMPLE_CATALOG)

    # Remove obsolete indexes
    for idx in ["getDistrict", "getProvince"]:
        if del_index(catalog, idx):
            logger.info("Removed index '%s' from sample catalog" % idx)

    # Remove obsolete metadata columns
    obsolete_columns = [
        "getClientURL",
        "getDistrict",
        "getPhysicalPath",
        "getProvince",
        "getTemplateURL",
    ]
    for col in obsolete_columns:
        if del_column(catalog, col):
            logger.info(
                "Removed column '%s' from sample catalog" % col
            )

    logger.info("Cleaning up sample catalog indexes and columns [DONE]")


@upgradestep(product, version)
def setup_sample_labels(tool):
    """Register ManageLabels permission and add labels KeywordIndex to
    senaite_catalog_sample. Reindex so labels on existing samples are
    queryable via the new index.
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    logger.info("Importing rolemap for ManageLabels permission ...")
    setup.runImportStepFromProfile(profile, "rolemap")

    logger.info("Adding 'labels' index to sample catalog ...")
    catalog = api.get_tool(SAMPLE_CATALOG)
    if add_catalog_index(catalog, "labels", "", "KeywordIndex"):
        logger.info("Reindexing 'labels' in sample catalog ...")
        reindex_index(SAMPLE_CATALOG, "labels")
        logger.info("Reindexing 'labels' in sample catalog [DONE]")

    logger.info("Adding 'getLabels' column to sample catalog ...")
    add_catalog_column(catalog, "getLabels")

    logger.info("Adding 'getColor' column to setup catalog ...")
    setup_catalog = api.get_tool(SETUP_CATALOG)
    add_catalog_column(setup_catalog, "getColor")
    # The pre-release of this PR used a bare 'color' attribute column;
    # drop it if present so the catalog reflects the final method-call
    # convention.
    if "color" in setup_catalog.schema():
        del_column(setup_catalog, "color")
    label_brains = setup_catalog(portal_type="Label")
    logger.info("Refreshing %s Label brains for color metadata "
                "and seeding rename-cascade baseline ..."
                % len(label_brains))
    # The label rename subscriber reads `PREVIOUS_TITLE_KEY` from
    # each Label's annotations to detect title changes; seed it for
    # every pre-existing Label so the *first* post-upgrade rename
    # actually cascades rather than being treated as the baseline.
    from senaite.core.config.labels import PREVIOUS_TITLE_KEY
    from zope.annotation.interfaces import IAnnotations
    for brain in label_brains:
        obj = api.get_object(brain, default=None)
        if obj is None:
            logger.warn("Could not wake Label brain '%s'" % brain.UID)
            continue
        # No idxs= so the metadata columns get refreshed too.
        obj.reindexObject()
        annotations = IAnnotations(obj)
        if PREVIOUS_TITLE_KEY not in annotations:
            annotations[PREVIOUS_TITLE_KEY] = api.safe_unicode(
                obj.title or u"")

    logger.info("Setup sample labels [DONE]")


@upgradestep(product, version)
def add_sample_catalog_indexes(tool):
    """Add new indexes to senaite_catalog_sample

    - getSampleTypeUID: FieldIndex for filtering samples by type UID.
    - getSamplePointUID: FieldIndex for filtering samples by sample point UID.
    - getAnalysesKeywords: KeywordIndex storing the keyword of every analysis
      contained in the sample and its partitions. Enables queries such as
      ``catalog(getAnalysesKeywords="glucose")`` to retrieve all samples that
      include a specific analysis.
    """
    logger.info("Adding new indexes to sample catalog ...")
    catalog = api.get_tool(SAMPLE_CATALOG)

    new_indexes = [
        ("getSampleTypeUID", "", "FieldIndex"),
        ("getSamplePointUID", "", "FieldIndex"),
        ("getAnalysesKeywords", "", "KeywordIndex"),
    ]
    for idx_id, idx_attr, idx_type in new_indexes:
        if add_catalog_index(catalog, idx_id, idx_attr, idx_type):
            logger.info("Reindexing '%s' in sample catalog ..." % idx_id)
            reindex_index(SAMPLE_CATALOG, idx_id)
            logger.info(
                "Reindexing '%s' in sample catalog [DONE]" % idx_id
            )

    logger.info("Adding new indexes to sample catalog [DONE]")


@upgradestep(product, version)
def strip_global_client_role(tool):
    """Remove directly-assigned global 'Client' role from users.

    The 'Client' role is now granted dynamically by the
    ILocalRoleProvider in `senaite.core.security.clientrole` based on
    the user's `linked_client_uid` member property. A user with the
    role assigned directly through the portal role manager but no
    contact link has the Client landing page but no Owner role on any
    client folder, which is a half-configured state with no useful
    access.

    Iterate the principals assigned the 'Client' role via the portal
    role manager and remove the direct assignment. Users keep the
    role dynamically wherever their `linked_client_uid` matches.
    """
    logger.info("Stripping global 'Client' role from users ...")
    acl = api.get_tool("acl_users")
    prm = getattr(acl, "portal_role_manager", None)
    if prm is None:
        logger.warn(
            "No portal_role_manager available; nothing to strip")
        return

    principals = prm.listAssignedPrincipals("Client")
    total = len(principals)
    logger.info(
        "Found %s principals with directly-assigned 'Client' role"
        % total)

    removed = 0
    for principal_id, _title in principals:
        try:
            prm.removeRoleFromPrincipal("Client", principal_id)
        except KeyError:
            logger.warn(
                "Could not remove 'Client' from '%s'" % principal_id)
            continue
        removed += 1
        logger.info(
            "Removed direct 'Client' role from '%s'" % principal_id)

    logger.info(
        "Stripped global 'Client' role from %s/%s principals"
        % (removed, total))


CLIENT_TREE_CATALOGS = (
    "senaite_catalog_sample",
    "senaite_catalog_analysis",
    "senaite_catalog",
    "senaite_catalog_report",
    "senaite_catalog_attachments",
    "senaite_catalog_client",
    "senaite_catalog_setup",
    "senaite_catalog_worksheet",
)


@upgradestep(product, version)
def reindex_dx_client_aware_allowed_roles(tool):
    """Re-run `reindex_client_tree_allowed_roles` after the
    `IClientAwareMixin` interface mismatch was fixed.

    #2934 wired the new `allowedRolesAndUsers` indexer, the
    dynamic client-role provider, and this very reindex step
    against `bika.lims.interfaces.IClientAwareMixin` (the AT
    marker). The DX `ClientAwareMixin` base class in
    `senaite.core.content.mixins`, however, implements the
    separate `senaite.core.interfaces.IClientAwareMixin`. The
    `providedBy` check in the original step therefore
    silently rejected every DX descendant -- including
    `SamplePoint`, `SampleType`, and `AnalysisProfile` -- and
    none of them ever received the new `client:<uid>` token.
    Catalog queries from client users (e.g. the Excel-import
    sample-point lookup) returned no hits even though the
    objects exist and direct traversal works via the dynamic
    role provider.

    All four call sites now import `IClientAwareMixin` from
    `senaite.core.interfaces`; this follow-up step iterates
    the client-tree catalogs again so every DX descendant
    picks up the missing token.
    """
    reindex_client_tree_allowed_roles()


@upgradestep(product, version)
def switch_to_dynamic_client_roles(tool):
    """Migrate persistent group/local-role access to the dynamic
    ILocalRoleProvider model.

    Three idempotent passes:

    1. Reindex `allowedRolesAndUsers` on every client-tree object so it
       picks up the new stable `client:<client_uid>` token.
    2. Backfill the `linked_client_uid` member property for every
       already-linked client contact, so the dynamic role provider can
       authorise those users without having to walk the catalog.
    3. Remove the orphan `auto_create_client_group` registry record
       (the field has been dropped from `IClientRegistry`).

    Existing per-client groups and persisted Owner local roles on the
    client folders are left untouched here; they are removed by the
    follow-up cleanup upgrade step.
    """
    portal = tool.aq_inner.aq_parent
    reindex_client_tree_allowed_roles()
    backfill_linked_client_uid()
    drop_auto_create_client_group_record(portal)


REINDEX_BATCH_SIZE = 100


def reindex_client_tree_allowed_roles():
    """Reindex `allowedRolesAndUsers` on every IClient + IClientAware
    object so they carry the new `client:<uid>` token.

    Bypasses `reindexObject` (and therefore the
    `CatalogMultiplexProcessor` queue) and writes the single index
    directly on every catalog the object lives in. Without this,
    the queue would re-fan the reindex to every mapped catalog at
    transaction-commit time, redo work that has just been done, and
    dominate the upgrade-step runtime on production-size datasets.

    Per-object: deactivate from the ZODB cache after the write to
    keep the cache from filling up over very large catalogs;
    savepoint every 5000 instead of every 500 because each item is
    a single index write with no metadata refresh.
    """
    from bika.lims.interfaces import IClient
    from senaite.core.interfaces import IClientAwareMixin

    logger.info("Reindexing allowedRolesAndUsers on client-tree content ...")
    seen = set()
    total = 0
    for catalog_id in CLIENT_TREE_CATALOGS:
        catalog = api.get_tool(catalog_id, default=None)
        if catalog is None:
            continue
        brains = catalog.unrestrictedSearchResults({})
        for brain in brains:
            uid = getattr(brain, "UID", None)
            if uid and uid in seen:
                continue
            try:
                obj = brain.getObject()
            except (AttributeError, KeyError):
                continue
            if obj is None:
                continue
            if not (IClient.providedBy(obj)
                    or IClientAwareMixin.providedBy(obj)):
                continue
            for cat in api.get_catalogs_for(obj):
                cat.catalog_object(
                    obj,
                    idxs=["allowedRolesAndUsers"],
                    update_metadata=False)
            try:
                obj._p_deactivate()
            except Exception as exc:
                # `_p_deactivate` is a cache-eviction optimisation;
                # failures here are non-fatal and the reindex above
                # has already persisted. Log at debug for
                # troubleshooting but do not interrupt the upgrade.
                logger.debug(
                    "_p_deactivate failed on %r: %s" % (obj, exc))
            if uid:
                seen.add(uid)
            total += 1
            if total % REINDEX_BATCH_SIZE == 0:
                transaction.savepoint(optimistic=True)
            if total % 500 == 0:
                logger.info("  ... reindexed %s objects" % total)
            if total % 5000 == 0:
                transaction.savepoint(optimistic=True)
    logger.info(
        "Reindexed allowedRolesAndUsers on %s client-tree objects" % total)


def backfill_linked_client_uid():
    """Set the `linked_client_uid` and `linked_contact_uid` user
    properties for every existing client contact already linked to a
    user account.

    Both properties drive different parts of the runtime: the client
    UID is what the dynamic local-role provider in
    `senaite.core.security.clientrole` reads to grant access on the
    client tree, while the contact UID is the back-reference that
    resolves a logged-in user to their contact object. The link path
    in `Contact._linkUser` writes both, so existing links must carry
    both for parity.
    """
    from bika.lims.interfaces import IClient
    from senaite.core.content.contact import CLIENT_UID_KEY
    from senaite.core.content.contact import CONTACT_UID_KEY
    from senaite.core.content.contact import _set_user_property

    logger.info(
        "Backfilling `linked_client_uid` and `linked_contact_uid` "
        "on linked users ...")
    contacts = api.search({"portal_type": "Contact"}, CONTACT_CATALOG)
    updated = 0
    for brain in contacts:
        contact = api.get_object(brain)
        parent = contact.aq_parent
        if not IClient.providedBy(parent):
            continue
        user = contact.getUser()
        if user is None:
            continue
        _set_user_property(user, CLIENT_UID_KEY, api.get_uid(parent))
        _set_user_property(user, CONTACT_UID_KEY, api.get_uid(contact))
        updated += 1
    logger.info(
        "Backfilled linked UID properties on %s users" % updated)


def drop_auto_create_client_group_record(portal):
    """Delete the obsolete `auto_create_client_group` registry record.

    The setting moved out of the registry when client access switched
    to the dynamic role provider. Leaving the record behind would
    only confuse future readers.
    """
    registry = api.get_tool("portal_registry", default=None)
    if registry is None:
        return
    key = ("senaite.core.registry.schema.IClientRegistry."
           "auto_create_client_group")
    if key in registry.records:
        del registry.records[key]
        logger.info("Removed orphan registry record '%s'" % key)


@upgradestep(product, version)
def remove_client_manage_access_action(tool):
    """Drop the `manage_access` action from the Client FTI.

    The action linked to @@sharing on every Client; sharing on the
    client tree is now disabled because access is granted dynamically
    by the ILocalRoleProvider. Removing the action prevents admins
    from clicking through to the (now NotFound) view.
    """
    types_tool = api.get_tool("portal_types")
    fti = types_tool.getTypeInfo("Client")
    if fti is None:
        return
    actions = list(fti.listActions())
    target_indices = [str(i) for i, a in enumerate(actions)
                      if a.id == "manage_access"]
    if not target_indices:
        return
    fti.deleteActions(target_indices)
    logger.info("Removed 'manage_access' action from Client FTI")


@upgradestep(product, version)
def remove_legacy_client_groups(tool):
    """Remove the per-client group + Owner local-role grant on every
    Client.

    Pre-2.7 SENAITE auto-created a group per Client (`Client.GROUP_KEY`
    stored the id on the client object) and granted that group the
    local Owner role on the client folder. With #2934 client users get
    Owner + Client dynamically via the ILocalRoleProvider, so the
    legacy group and its persisted local-role grant are dead weight.

    For each Client:

    1. Find the stored group id and the matching group in
       portal_groups. Skip the client if no id is stored or the group
       no longer exists.
    2. Skip the client if the persisted group id no longer matches the
       client's own stored ``_client_group_id`` — protects against an
       admin who renamed the group manually.
    3. Remove the corresponding entry from ``__ac_local_roles__`` on
       the client folder via ``manage_delLocalRoles``. This triggers
       ``reindexObjectSecurity`` recursively so the stale
       ``user:<group_id>`` token drops out of ``allowedRolesAndUsers``
       on every descendant. One-time cost; the new ``client:<uid>``
       token added by #2934 already carries client access from here on.
    4. Remove the group from portal_groups.
    5. Clear the ``_client_group_id`` attribute on the client.
    """
    portal_groups = api.get_tool("portal_groups")
    clients = api.search({"portal_type": "Client"}, CLIENT_CATALOG)
    total = len(clients)
    removed_groups = 0
    cleared_local_roles = 0
    for num, brain in enumerate(clients, start=1):
        client = api.get_object(brain)
        if num % 50 == 0:
            logger.info("Cleaning client groups: %s/%s" % (num, total))
        group_id = getattr(client, "_client_group_id", None)
        if not group_id:
            continue
        if group_id in (client.__ac_local_roles__ or {}):
            client.manage_delLocalRoles([group_id])
            # `manage_delLocalRoles` only mutates `__ac_local_roles__`;
            # the catalog still carries the stale `user:<group_id>`
            # token on every descendant until reindexObjectSecurity
            # walks the subtree. Paying the cost once here is the whole
            # point of this upgrade step.
            client.reindexObjectSecurity()
            cleared_local_roles += 1
            logger.info(
                "Cleared Owner local role for group '%s' on client '%s'"
                % (group_id, client.getName()))
        group = portal_groups.getGroupById(group_id)
        if group is not None:
            portal_groups.removeGroup(group_id)
            removed_groups += 1
            logger.info(
                "Removed legacy client group '%s' for client '%s'"
                % (group_id, client.getName()))
        try:
            delattr(client, "_client_group_id")
        except AttributeError:
            pass
    logger.info(
        "Legacy client-group cleanup: %s groups removed, "
        "%s local-role grants cleared on %s clients"
        % (removed_groups, cleared_local_roles, total))


@upgradestep(product, version)
def drop_client_catalog_group_id_column(tool):
    """Drop the `getGroupId` metadata column from `senaite_catalog_client`.

    The column mirrored the legacy per-client group id. After the
    dynamic role provider replaces the group mechanism, the column is
    dead weight and every brain that still carries a stale value
    misleads any code that reads it.
    """
    catalog = api.get_tool("senaite_catalog_client", default=None)
    if catalog is None:
        return
    if del_column(catalog, "getGroupId"):
        logger.info(
            "Dropped 'getGroupId' column from senaite_catalog_client")


@upgradestep(product, version)
def remove_client_sharing_alias(tool):
    """Drop the `sharing` method alias from the Client FTI.

    The alias used to route `/<client>/sharing` to `@@sharing`. The
    `manage_access` action that exposed it was removed by
    `remove_client_manage_access_action`, but the alias itself kept
    the view reachable by direct URL. Sharing on the client tree is
    redundant now that access is granted dynamically.
    """
    types_tool = api.get_tool("portal_types")
    fti = types_tool.getTypeInfo("Client")
    if fti is None:
        return
    aliases = dict(fti.getMethodAliases() or {})
    if "sharing" not in aliases:
        return
    del aliases["sharing"]
    fti.setMethodAliases(aliases)
    logger.info("Removed 'sharing' method alias from Client FTI")
