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


from datetime import timedelta

from bika.lims import api
from bika.lims.api import safe_unicode as u
from bika.lims.interfaces import IInvalidated
from bika.lims.utils import tmpID
from plone.app.blob.field import BlobWrapper
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContent
from plone.namedfile.file import NamedBlobFile
from senaite.core import logger
from senaite.core.api import dtime
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import CONTACT_CATALOG
from senaite.core.catalog import REPORT_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.catalog.analysis_catalog import INDEXES as ANALYSIS_INDEXES
from senaite.core.config import PROJECTNAME as product
from senaite.core.interfaces import IContentMigrator
from senaite.core.interfaces.catalog import ISenaiteCatalogObject
from senaite.core.schema.addressfield import NAIVE_ADDRESS
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.schema.addressfield import POSTAL_ADDRESS
from senaite.core.setuphandlers import _run_import_step
from senaite.core.setuphandlers import add_catalog_column
from senaite.core.setuphandlers import add_catalog_index
from senaite.core.setuphandlers import add_dexterity_items
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.upgrade.utils import permanently_allow_type_for
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

version = "2.7.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

REMOVE_AT_TYPES = [
    "ARReport",
    "Contact",
    "Multifile",
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


@upgradestep(product, version)
def import_rolemap(tool):
    """Import rolemap step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    setup.runImportStepFromProfile(profile, "rolemap")


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
    remove_at_portal_types(tool)

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


@upgradestep(product, version)
def migrate_contacts_to_dx(tool):
    """Migrate Contact objects from Archetypes to Dexterity
    """
    logger.info("Migrating Contacts to Dexterity ...")

    # Ensure old AT types are flushed first
    remove_at_portal_types(tool)

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
    remove_at_portal_types(tool)

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
    remove_at_portal_types(tool)

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
    remove_at_portal_types(tool)
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
    remove_at_portal_types(tool)
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

        if num % 100 == 0:
            logger.info("Progress: {}/{} reports migrated".format(num, total))

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
