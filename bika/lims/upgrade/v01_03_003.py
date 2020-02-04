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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from collections import defaultdict
from operator import itemgetter

import transaction
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME as product
from bika.lims.interfaces import IAnalysisRequestWithPartitions
from bika.lims.interfaces import ISubmitted
from bika.lims.interfaces import IVerified
from bika.lims.setuphandlers import add_dexterity_setup_items
from bika.lims.setuphandlers import setup_form_controller_actions
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from Products.Archetypes.config import UID_CATALOG
from zope.interface import alsoProvides

version = "1.3.3"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

INDEXES_TO_ADD = [
    # Replaces getSampleTypeUIDs
    ("bika_setup_catalog", "sampletype_uid", "KeywordIndex"),

    # Replaces getSampleTypeTitle
    ("bika_setup_catalog", "sampletype_title", "KeywordIndex"),

    # Replaces getAvailableMethodUIDs
    # Used to filter services in Worksheet's Add Analyses View for when the
    # Worksheet Template being used has a Method assigned
    ("bika_setup_catalog", "method_available_uid", "KeywordIndex"),

    # Replaces getInstrumentTitle
    # Used for sorting Worksheet Templates listing by Instrument
    ("bika_setup_catalog", "instrument_title", "KeywordIndex"),

    # Replaces getPrice, getTotalPrice, getVolume
    # Used for sorting LabProducts listing
    ("bika_setup_catalog", "price", "FieldIndex"),
    ("bika_setup_catalog", "price_total", "FieldIndex"),

    # Replaces getInstrumentTypeName
    ("bika_setup_catalog", "instrumenttype_title", "KeywordIndex"),

    # Replaces getDepartmentTitle
    ("bika_setup_catalog", "department_title", "KeywordIndex"),

    # Replaces getPointOfCapture
    ("bika_setup_catalog", "point_of_capture", "FieldIndex"),

    # Replaces getDepartmentUID
    ("bika_setup_catalog", "department_uid", "KeywordIndex"),

    # Default listing_searchable_text index adapter for setup_catalog
    ("bika_setup_catalog", "listing_searchable_text", "TextIndexNG3"),

    # Default listing_searchable_text index adapter for setup_catalog
    ("bika_setup_catalog", "category_uid", "KeywordIndex"),
]

INDEXES_TO_REMOVE = [
    # Only used in add2 to filter Sample Points by Sample Type when a Sample
    # Type was selected. Now, getSampleTypeUID is used instead because of
    ("bika_setup_catalog", "getSampleTypeTitles"),

    # Only used for when Sample and SamplePartition objects
    # existed. The following are the portal types stored in bika_catalog:
    #   Batch, BatchFolder and ReferenceSample
    # and there are no searches by getSampleTypeTitle for none of them
    ("bika_catalog", "getSampleTypeTitle"),

    # Not used neither for searches nor filtering of any of the content types
    # stored in bika_catalog (Batch, BatchFolder and ReferenceSample)
    ("bika_catalog", "getSampleTypeUID"),

    # getAccredited was only used in the "hidden" view accreditation to filter
    # services labeled as "accredited". Since we don't expect that listing to
    # contain too many items, they are now filtered by waking-up the object
    ("bika_setup_catalog", "getAccredited"),

    # getAnalyst index is used in Analyses (Duplicates and Reference included)
    # and Worksheets. None of the types stored in setup_catalog support Analyst
    ("bika_setup_catalog", "getAnalyst"),

    # getBlank index is not used in setup_catalog, but in bika_catalog, where
    # is used in AddControl and AddBlank views (Worksheet)
    ("bika_setup_catalog", "getBlank"),

    # Only used in analyses listing, but from analysis_catalog
    ("bika_setup_catalog", "getCalculationUID"),

    # Only used for sorting in LabContacts listing. Replaced by sortable_title
    ("bika_setup_catalog", "getFullname"),

    # Used in analysis_catalog, but not in setup_catalog
    ("bika_setup_catalog", "getServiceUID"),

    # Not used anywhere
    ("bika_setup_catalog", "getDocumentID"),
    ("bika_setup_catalog", "getDuplicateVariation"),
    ("bika_setup_catalog", "getFormula"),
    ("bika_setup_catalog", "getInstrumentLocationName"),
    ("bika_setup_catalog", "getInstrumentType"),
    ("bika_setup_catalog", "getHazardous"),
    ("bika_setup_catalog", "getManagerEmail"),
    ("bika_setup_catalog", "getManagerPhone"),
    ("bika_setup_catalog", "getManagerName"),
    ("bika_setup_catalog", "getMethodID"),
    ("bika_setup_catalog", "getMaxTimeAllowed"),
    ("bika_setup_catalog", "getModel"),
    ("bika_setup_catalog", "getCalculationTitle"),
    ("bika_setup_catalog", "getCalibrationExpiryDate"),
    ("bika_setup_catalog", "getVATAmount"),
    ("bika_setup_catalog", "getUnit"),
    ("bika_setup_catalog", "getSamplePointTitle"),
    ("bika_setup_catalog", "getVolume"),
    ("bika_setup_catalog", "getSamplePointUID"),
    ("bika_setup_catalog", "getCategoryTitle"),
    ("bika_setup_catalog", "cancellation_state"),
    ("bika_setup_catalog", "getName"),
    ("bika_setup_catalog", "getServiceUIDs"),
    ("bika_setup_catalog", "SearchableText"),


    # REPLACEMENTS (indexes to be removed because of a replacement)

    # getSampleTypeUID --> sampletype_uid (FieldIndex --> KeywordIndex)
    ("bika_setup_catalog", "getSampleTypeUID"),
    ("bika_setup_catalog", "sampletype_uids"),

    # getSampleTypeTitle --> sampletype_title
    ("bika_setup_catalog", "getSampleTypeTitle"),

    # getAvailableMethodUIDs --> method_available_uid
    ("bika_setup_catalog", "getAvailableMethodUIDs"),

    # getInstrumentTitle --> instrument_title
    ("bika_setup_catalog", "getInstrumentTitle"),

    # getPrice --> price
    ("bika_setup_catalog", "getPrice"),

    # getTotalPrice --> price_total
    ("bika_setup_catalog", "getTotalPrice"),

    # getInstrumentTypeName --> instrumenttype_title
    ("bika_setup_catalog", "getInstrumentTypeName"),

    # getDepartmentTitle --> department_title
    ("bika_setup_catalog", "getDepartmentTitle"),

    # getPointOfCapture --> point_of_capture
    ("bika_setup_catalog", "getPointOfCapture"),

    # getDepartmentUID --> department_uid
    ("bika_setup_catalog", "getDepartmentUID"),

    # getCategoryUID --> category_uid
    ("bika_setup_catalog", "getCategoryUID"),

]

METADATA_TO_REMOVE = [
    # Not used anywhere. In SamplePoints and Specifications listings, the
    # SampleType object is waken-up instead of calling the metadata
    ("bika_setup_catalog", "getSampleTypeTitle"),

    # getSampleTypeUID (as metadata field) is only used for analyses and
    # samples (AnalysisRequest), and none of the two are stored in setup_catalog
    ("bika_setup_catalog", "getSampleTypeUID"),

    # Only used for when Sample and SamplePartition objects existed.
    # The following are the portal types stored in bika_catalog:
    #   Batch, BatchFolder and ReferenceSample
    # and "getSampleTypeTitle" metadata is not used for none of them
    ("bika_catalog", "getSampleTypeTitle"),

    # Not used anywhere
    ("bika_setup_catalog", "getAccredited"),

    # Not used anywhere
    ("bika_setup_catalog", "getBlank"),
    ("bika_setup_catalog", "getDuplicateVariation"),
    ("bika_setup_catalog", "getFormula"),
    ("bika_setup_catalog", "getInstrumentLocationName"),
    ("bika_setup_catalog", "getInstrumentTitle"),
    ("bika_setup_catalog", "getPrice"),
    ("bika_setup_catalog", "getTotalPrice"),
    ("bika_setup_catalog", "getVolume"),
    ("bika_setup_catalog", "getInstrumentTypeName"),
    ("bika_setup_catalog", "getInstrumentType"),
    ("bika_setup_catalog", "getHazardous"),
    ("bika_setup_catalog", "getManagerEmail"),
    ("bika_setup_catalog", "getManagerPhone"),
    ("bika_setup_catalog", "getManagerName"),
    ("bika_setup_catalog", "getMaxTimeAllowed"),
    ("bika_setup_catalog", "getModel"),
    ("bika_setup_catalog", "getCalculationTitle"),
    ("bika_setup_catalog", "getCalculationUID"),
    ("bika_setup_catalog", "getCalibrationExpiryDate"),
    ("bika_setup_catalog", "getDepartmentTitle"),
    ("bika_setup_catalog", "getVATAmount"),
    ("bika_setup_catalog", "getUnit"),
    ("bika_setup_catalog", "getPointOfCapture"),
    ("bika_setup_catalog", "getSamplePointUID"),
    ("bika_setup_catalog", "getFullname"),
    ("bika_setup_catalog", "cancellation_state"),
    ("bika_setup_catalog", "getName"),
    ("bika_setup_catalog", "getServiceUID"),

    # Was only used in analyses listing, but it can lead to inconsistencies
    # because there are some analyses (Duplicates) their result range depends
    # on the result of an original analysis. Thus, better to remove the metadata
    # and wake-up object than add additional reindexes, etc. everywhere
    (CATALOG_ANALYSIS_LISTING, "getResultsRange")
]


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------

    # Moved all Viewlets from senaite.lims to senaite.core
    setup.runImportStepFromProfile(profile, "viewlets")

    # https://github.com/senaite/senaite.core/issues/1504
    remove_cascaded_analyses_of_root_samples(portal)

    # Add additional JavaScripts to registry
    # https://github.com/senaite/senaite.core/pull/1502
    setup.runImportStepFromProfile(profile, "jsregistry")

    # Fix Site Properties Generic Setup Export Step
    # https://github.com/senaite/senaite.core/pull/1469
    setup.runImportStepFromProfile(profile, "propertiestool")

    # Remove, rename and add indexes/metadata
    # https://github.com/senaite/senaite.core/pull/1486
    cleanup_indexes_and_metadata(portal)

    # Sample edit form (some selection widgets empty)
    # Reindex client's related fields (getClientUID, getClientTitle, etc.)
    # https://github.com/senaite/senaite.core/pull/1477
    reindex_client_fields(portal)

    # Redirect to worksheets folder when a Worksheet is removed
    # https://github.com/senaite/senaite.core/pull/1480
    setup_form_controller_actions(portal)

    # Mark primary samples with IAnalysisRequestPrimary
    mark_samples_with_partitions(portal)

    # Add the dynamic analysisspecs folder
    # https://github.com/senaite/senaite.core/pull/1492
    setup.runImportStepFromProfile(profile, "typeinfo")
    setup.runImportStepFromProfile(profile, "controlpanel")
    add_dexterity_setup_items(portal)

    # Reset the results ranges from Specification objects (to include uid)
    # https://github.com/senaite/senaite.core/pull/1506
    reset_specifications_ranges(portal)

    # Update the ResultsRange field from Samples and their analyses as needed
    # https://github.com/senaite/senaite.core/pull/1506
    update_samples_result_ranges(portal)

    # Try to install the spotlight add-on
    # https://github.com/senaite/senaite.core/pull/1517
    install_senaite_core_spotlight(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_cascaded_analyses_of_root_samples(portal):
    """Removes Analyses from Root Samples that belong to Partitions

    https://github.com/senaite/senaite.core/issues/1504
    """
    logger.info("Removing cascaded analyses from Root Samples...")

    # Query all root Samples
    query = {
        "isRootAncestor": True,
        "sort_on": "created",
        "sort_order": "ascending",
    }
    root_samples = api.search(query, "bika_catalog_analysisrequest_listing")
    total = len(root_samples)
    logger.info("{} Samples to check... ".format(total))

    to_clean = []

    for num, brain in enumerate(root_samples):
        logger.debug("Checking Root Sample {}/{}".format(num+1, total))

        # No Partitions, continue...
        if not brain.getDescendantsUIDs:
            continue

        # get the root sample
        root_sample = api.get_object(brain)
        # get the contained analyses of the root sample
        root_analyses = root_sample.objectIds(spec=["Analysis"])

        # Mapping of cascaded Analysis -> Partition
        analysis_mapping = {}

        # check if a root analysis is located as well in one of the partitions
        for partition in root_sample.getDescendants():
            # get the contained analyses of the partition
            part_analyses = partition.objectIds(spec=["Analysis"])
            # filter analyses that cascade root analyses
            cascaded = filter(lambda an: an in root_analyses, part_analyses)
            # keep a mapping of analysis -> partition
            for analysis in cascaded:
                analysis_mapping[analysis] = partition

        if analysis_mapping:
            to_clean.append((root_sample, analysis_mapping))

    # count the cases for each condition
    case_counter = defaultdict(int)

    # cleanup cascaded analyses
    # mapping maps the analysis id -> partition
    for sample, mapping in to_clean:

        # go through the cascaded analyses and decide if the cascaded analysis
        # should be removed from (a) the root sample or (b) the partition.

        for analysis_id, partition in mapping.items():

            # analysis from the root sample
            root_an = sample[analysis_id]
            # WF state from the root sample analysis
            root_an_state = api.get_workflow_status_of(root_an)

            # analysis from the partition sample
            part_an = partition[analysis_id]
            # WF state from the partition sample analysis
            part_an_state = api.get_workflow_status_of(part_an)

            case_counter["{}_{}".format(root_an_state, part_an_state)] += 1

            # both analyses have the same WF state
            if root_an_state == part_an_state:
                # -> remove the analysis from the root sample
                sample._delObject(analysis_id)
                logger.info(
                    "Remove analysis '{}' in state '{}' from sample {}: {}"
                    .format(analysis_id, root_an_state,
                            api.get_id(sample), api.get_url(sample)))

            # both are in verified/published state
            elif IVerified.providedBy(root_an) and IVerified.providedBy(part_an):
                root_an_result = root_an.getResult()
                part_an_result = root_an.getResult()
                if root_an_result == part_an_result:
                    # remove the root analysis
                    sample._delObject(analysis_id)
                    logger.info(
                        "Remove analysis '{}' in state '{}' from sample {}: {}"
                        .format(analysis_id, root_an_state,
                                api.get_id(sample), api.get_url(sample)))
                else:
                    # -> unsolvable edge case
                    #    display an error message
                    logger.error(
                        "Analysis '{}' of root sample in state '{}' "
                        "and Analysis of partition in state {}. "
                        "Please fix manually: {}"
                        .format(analysis_id, root_an_state, part_an_state,
                                api.get_url(sample)))

            # root analysis is in invalid state
            elif root_an_state in ["rejected", "retracted"]:
                # -> probably the retest was automatically created in the
                #    parent instead of the partition
                pass

            # partition analysis is in invalid state
            elif part_an_state in ["rejected", "retracted"]:
                # -> probably the retest was automatically created in the
                #    parent instead of the partition
                pass

            # root analysis was submitted, but not the partition analysis
            elif ISubmitted.providedBy(root_an) and not ISubmitted.providedBy(part_an):
                # -> remove the analysis from the partition
                partition._delObject(analysis_id)
                logger.info(
                    "Remove analysis '{}' in state '{}' from partition {}: {}"
                    .format(analysis_id, part_an_state,
                            api.get_id(partition), api.get_url(partition)))

            # partition analysis was submitted, but not the root analysis
            elif ISubmitted.providedBy(part_an) and not ISubmitted.providedBy(root_an):
                # -> remove the analysis from the root sample
                sample._delObject(analysis_id)
                logger.info(
                    "Remove analysis '{}' in state '{}' from sample {}: {}"
                    .format(analysis_id, root_an_state,
                            api.get_id(sample), api.get_url(sample)))

            # inconsistent state
            else:
                logger.warning(
                    "Can not handle analysis '{}' located in '{}' (state {}) and '{}' (state {})"
                    .format(analysis_id,
                            repr(sample), root_an_state,
                            repr(partition), part_an_state))

    logger.info("Removing cascaded analyses from Root Samples... [DONE]")

    logger.info("State Combinations (root_an_state, part_an_state): {}"
                .format(sorted(case_counter.items(), key=itemgetter(1), reverse=True)))


def reindex_client_fields(portal):
    logger.info("Reindexing client fields ...")
    fields_to_reindex = [
        "getClientUID",
        "getClientID",
        "getClientTitle",
        "getClientURL"
    ]

    # We only need to reindex those that might be associated to a Client object.
    # There is no need to reindex objects that already belong to a Client.
    # Batches were correctly indexed in previous upgrade step
    portal_types = [
        "AnalysisProfile",
        "AnalysisSpec",
        "ARTemplate",
        "SamplePoint"
    ]

    query = dict(portal_type=portal_types)
    brains = api.search(query, UID_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Reindexing client fields: {}/{}".format(num, total))

        obj = api.get_object(brain)
        obj.reindexObject(idxs=fields_to_reindex)

    logger.info("Reindexing client fields ... [DONE]")


def cleanup_indexes_and_metadata(portal):
    # Remove stale indexes and metadata
    remove_stale_indexes(portal)
    remove_stale_metadata(portal)

    # Add new indexes
    add_new_indexes(portal)

    # Some indexes in setup_catalog changed
    reindex_labcontact_sortable_title(portal)
    reindex_supplier_manufacturers_titles(portal)


def reindex_labcontact_sortable_title(portal):
    logger.info("Reindexing sortable_title for LabContacts ...")
    query = dict(portal_type="LabContact")
    for brain in api.search(query, SETUP_CATALOG):
        obj = api.get_object(brain)
        obj.reindexObject(idxs=["sortable_title"])
    logger.info("Reindexing sortable_title for LabContacts ... [DONE]")


def reindex_supplier_manufacturers_titles(portal):
    logger.info("Reindexing title indexes for Suppliers and Manufacturers ...")
    query = dict(portal_type="Supplier")
    for brain in api.search(query, SETUP_CATALOG):
        obj = api.get_object(brain)
        obj.reindexObject(idxs=["title", "sortable_title"])
    logger.info("Reindexing title indexes for Suppliers and Manufacturers ... [DONE]")


def remove_stale_indexes(portal):
    logger.info("Removing stale indexes ...")
    for catalog, index in INDEXES_TO_REMOVE:
        del_index(catalog, index)
    logger.info("Removing stale indexes ... [DONE]")


def remove_stale_metadata(portal):
    logger.info("Removing stale metadata ...")
    for catalog, column in METADATA_TO_REMOVE:
        del_metadata(catalog, column)
    logger.info("Removing stale metadata ... [DONE]")


def del_index(catalog_id, index_name):
    logger.info("Removing '{}' index from '{}' ..."
                .format(index_name, catalog_id))
    catalog = api.get_tool(catalog_id)
    if index_name not in catalog.indexes():
        logger.info("Index '{}' not in catalog '{}' [SKIP]"
                    .format(index_name, catalog_id))
        return
    catalog.delIndex(index_name)


def del_metadata(catalog_id, column):
    logger.info("Removing '{}' metadata from '{}' ..."
                .format(column, catalog_id))
    catalog = api.get_tool(catalog_id)
    if column not in catalog.schema():
        logger.info("Metadata '{}' not in catalog '{}' [SKIP]"
                    .format(column, catalog_id))
        return
    catalog.delColumn(column)


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


def mark_samples_with_partitions(portal):
    logger.info("Marking Samples with partitions ...")
    query = dict(portal_type="AnalysisRequest", isRootAncestor=False)
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Marking samples with partitions: {}/{}"
                        .format(num, total))
            transaction.commit()
        part = api.get_object(brain)
        parent = part.getParentAnalysisRequest()
        if not parent:
            logger.error("Partition w/o Parent: {}".format(api.get_id(part)))

        elif not IAnalysisRequestWithPartitions.providedBy(parent):
            alsoProvides(parent, IAnalysisRequestWithPartitions)

    logger.info("Marking Samples with partitions [DONE]")


def reset_specifications_ranges(portal):
    """Reset the result ranges to existing Specification objects. Prior
    versions were not storing the service uid in the result range
    """
    logger.info("Add uids to Specification ranges subfields ...")
    specifications = portal.bika_setup.bika_analysisspecs
    for specification in specifications.objectValues("AnalysisSpec"):
        specification.setResultsRange(specification.getResultsRange())
    logger.info("Add uids to Specification ranges subfields [DONE]")


def update_samples_result_ranges(portal):
    """Stores the result range field for those samples that have a
    specification assigned. In prior versions, getResultsRange was relying
    on Specification's ResultsRange
    """
    query = dict(portal_type="AnalysisRequest")
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 1000 == 0:
            logger.info("{}/{} samples processed ...".format(num, total))
            transaction.commit()
            logger.info("Changes commited")
        sample = api.get_object(brain)

        # Check if the ResultsRange field from sample contains values already
        ar_range = sample.getResultsRange()
        if ar_range:
            # This sample has results range already set, probably assigned
            # manually through Manage analyses
            # Reassign the results range (for uid subfield resolution)
            field = sample.getField("ResultsRange")
            field.set(sample, ar_range)

            # Store the result range directly to their analyses
            update_analyses_results_range(sample)

            # No need to go further
            continue

        # Check if the Sample has Specification set
        spec_uid = sample.getRawSpecification()
        if not spec_uid:
            # This sample does not have a specification set, skip
            continue

        # Store the specification results range to the Sample
        specification = sample.getSpecification()
        result_range = specification.getResultsRange()
        sample.getField("ResultsRange").set(sample, result_range)

        # Store the result range directly to their analyses
        update_analyses_results_range(sample)


def update_analyses_results_range(sample):
    field = sample.getField("ResultsRange")
    for analysis in sample.objectValues("Analysis"):
        service_uid = analysis.getRawAnalysisService()
        analysis_rr = field.get(sample, search_by=service_uid)
        if analysis_rr:
            analysis = api.get_object(analysis)
            analysis.setResultsRange(analysis_rr)


def install_senaite_core_spotlight(portal):
    """Install the senaite.core.spotlight addon
    """
    qi = api.get_tool("portal_quickinstaller")
    profile = "senaite.core.spotlight"
    if profile not in qi.listInstallableProfile():
        logger.error("Profile '{}' not found. Forgot to run buildout?"
                     .format(profile))
        return
    if qi.isProductInstalled(profile):
        logger.info("'{}' is installed".format(profile))
        return
    qi.installProduct(profile)
