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

import transaction

from bika.lims import api
from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from Products.Archetypes.config import REFERENCE_CATALOG
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields.uidreferencefield import get_storage

version = "1.3.6"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)


METADATA_TO_REMOVE = [
    # No longer used, see https://github.com/senaite/senaite.core/pull/2051/
    (CATALOG_ANALYSIS_LISTING, "getAnalyst"),
    (CATALOG_ANALYSIS_LISTING, "getAnalystName"),
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
    setup.runImportStepFromProfile(profile, "typeinfo")
    setup.runImportStepFromProfile(profile, "rolemap")

    remove_stale_metadata(portal)

    fix_samples_primary(portal)
    fix_worksheets_analyses(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_stale_metadata(portal):
    """Remove metadata columns no longer used
    """
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


def fix_samples_primary(portal):
    logger.info("Fix AnalysisRequests PrimaryAnalysisRequest ...")
    ref_id = "AnalysisRequestParentAnalysisRequest"
    ref_tool = api.get_tool(REFERENCE_CATALOG)
    query = {
        "portal_type": "AnalysisRequest",
        "isRootAncestor": False
    }
    samples = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(samples)
    for num, sample in enumerate(samples):
        if num and num % 100 == 0:
            logger.info("Processed samples: {}/{}".format(num, total))
        if num and num % 1000 == 0:
            transaction.commit()

        # Extract the parent(s) from this sample
        sample = api.get_object(sample)
        parents = sample.getRefs(relationship=ref_id)
        if not parents:
            # Processed already
            sample._p_deactivate()
            continue

        # Re-assign the parent sample(s)
        sample.setParentAnalysisRequest(parents)

        # Remove this relationship from reference catalog
        ref_tool.deleteReferences(sample, relationship=ref_id)

        # Reindex both the partition and parent(s)
        sample.reindexObject()
        for primary_sample in parents:
            primary_sample.reindexObject()

    logger.info("Fix AnalysisRequests PrimaryAnalysisRequest [DONE]")


def fix_worksheets_analyses(portal):
    logger.info("Fix Worksheets Analyses ...")
    worksheets = portal.worksheets.objectValues()
    total = len(worksheets)
    for num, worksheet in enumerate(worksheets):
        if num and num % 10 == 0:
            logger.info("Processed worksheets: {}/{}".format(num, total))
        fix_worksheet_analyses(worksheet)
    logger.info("Fix Worksheets Analyses [DONE]")


def fix_worksheet_analyses(worksheet):
    """Purge worksheet analyses based on the layout and removes the obsolete
    relationship from reference_catalog
    """
    # Get the referenced analyses via relationship
    analyses = worksheet.getRefs(relationship="WorksheetAnalysis")
    # Purge non-valid records
    # Fixes APIError: None is not supported
    analyses = filter(None, analyses)
    analyses_uids = [api.get_uid(an) for an in analyses]

    new_layout = []
    for slot in worksheet.getLayout():
        uid = slot.get("analysis_uid")
        if not api.is_uid(uid):
            continue

        if uid not in analyses_uids:
            if is_orphan(uid):
                continue

        new_layout.append(slot)

    # Re-assign the analyses
    uids = [slot.get("analysis_uid") for slot in new_layout]
    worksheet.setAnalyses(uids)
    worksheet.setLayout(new_layout)

    # Remove all records for this worksheet from reference catalog
    tool = api.get_tool(REFERENCE_CATALOG)
    tool.deleteReferences(worksheet, relationship="WorksheetAnalysis")


def is_orphan(uid):
    """Returns whether a counterpart object exists for the given UID
    """
    obj = api.get_object_by_uid(uid, None)
    return obj is None


def migrate_analysisrequest_referencefields(tool):
    """Migrates the ReferenceField from AnalysisRequest to UIDReferenceField
    """
    logger.info("Migrate ReferenceFields to UIDReferenceField ...")
    field_names = [
        "Attachment",
        "Batch",
        "CCContact",
        "Client",
        "DefaultContainerType",
        "DetachedFrom",
        "Invalidated",
        "Invoice",
        "PrimaryAnalysisRequest",
        "Profile",
        "Profiles",
        "PublicationSpecification",
        "Specification",
        "SubGroup",
        "Template",
    ]

    cat = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    brains = cat(portal_type="AnalysisRequest")
    total = len(brains)
    for num, sample in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Processed samples: {}/{}".format(num, total))

        if num and num % 1000 == 0:
            # reduce memory size of the transaction
            transaction.savepoint()

        # Migrate the reference fields for current sample
        sample = api.get_object(sample)
        migrate_reference_fields(sample, field_names)

        # Flush the object from memory
        sample._p_deactivate()

    logger.info("Migrate ReferenceFields to UIDReferenceField [DONE]")


def migrate_reference_fields(obj, field_names):
    """Migrates the reference fields with the names specified from the obj
    """
    ref_tool = api.get_tool(REFERENCE_CATALOG)
    for field_name in field_names:

        # Get the relationship id from field
        field = obj.getField(field_name)
        ref_id = field.get_relationship_key(obj)
        if not ref_id:
            logger.error("No relationship for field {}".format(field_name))

        # Extract the referenced objects
        references = obj.getRefs(relationship=ref_id)
        if not references:
            # Processed already or no referenced objects
            continue

        # Re-assign the object directly to the field
        if field.multiValued:
            value = [api.get_uid(val) for val in references]
        else:
            value = api.get_uid(references[0])
        field.set(obj, value)

        # Remove this relationship from reference catalog
        ref_tool.deleteReferences(obj, relationship=ref_id)


def rename_retestof_relationship(tool):
    """Renames the relationship for field RetestOf from the format
    '<portal-type>RetestOf' to 'AnalysisRetestOf'. This field is inherited by
    different analysis-like types and since we now assume that if no
    relationship is explicitly set, UIDReferenceField does not keep
    back-references, we need to update the relationship for those objects that
    are not from 'Analysis' portal_type
    """
    logger.info("Rename RetestOf relationship ...")
    uc = api.get_tool("uid_catalog")
    portal_types = ["DuplicateAnalysis", "ReferenceAnalysis", "RejectAnalysis"]
    brains = uc(portal_type=portal_types)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Rename RetestOf relationship {}/{}"
                        .format(num, total))

        if num and num % 1000 == 0:
            transaction.savepoint()

        # find out if the current analysis is a retest
        obj = api.get_object(brain)
        field = obj.getField("RetestOf")
        retest_of = field.get(obj)
        if retest_of:
            # remove the back-reference with the old relationship name
            portal_type = api.get_portal_type(obj)
            old_relationship_key = "{}RetestOf".format(portal_type)
            back_storage = get_storage(retest_of)
            back_storage.pop(old_relationship_key, None)

            # re-link referenced object with the new relationship name
            field.link_reference(retest_of, obj)

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Rename RetestOf relationship [DONE]")


def purge_backreferences(tool):
    """Purges back-references that are no longer required
    """
    logger.info("Purge no longer required back-references ...")
    portal_types = [
        "Analysis",
        "AnalysisRequest",
        "AnalysisService",
        "AnalysisSpec",
        "ARReport",
        "Batch",
        "Calculation",
        "DuplicateAnalysis",
        "Instrument",
        "LabContact",
        "Laboratory",
        "Method",
        "ReferenceAnalysis",
        "RejectAnalysis"
        "Worksheet",
    ]

    uc = api.get_tool("uid_catalog")
    brains = uc(portal_type=portal_types)
    total = len(brains)
    for num, obj in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Processed objects: {}/{}".format(num, total))

        if num and num % 1000 == 0:
            # reduce memory size of the transaction
            transaction.savepoint()

        # Purge back-references to given object
        obj = api.get_object(obj)
        purge_backreferences_to(obj)

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Purge no longer required back-references [DONE]")


def purge_backreferences_to(obj):
    """Removes back-references that are no longer needed that point to the
    given object
    """
    fields = api.get_fields(obj)
    portal_type = api.get_portal_type(obj)

    for field_name, field in fields.items():
        if not isinstance(field, UIDReferenceField):
            continue

        # Only purge if back-references are not required
        if field.keep_backreferences:
            continue

        # Get the referenced objects
        references = field.get(obj)
        if not isinstance(references, (list, tuple)):
            references = [references]

        # Remove the back-references from these referenced objects to current
        relationship = "{}{}".format(portal_type, field.getName())
        references = filter(None, references)
        for reference in references:
            back_storage = get_storage(reference)
            back_storage.pop(relationship, None)
