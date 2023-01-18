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
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

import transaction

from bika.lims import api
from bika.lims import LDL
from bika.lims import UDL
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields.uidreferencefield import get_storage
from bika.lims.interfaces import IRejected
from bika.lims.interfaces import IRetracted
from Products.Archetypes.config import REFERENCE_CATALOG
from senaite.core import logger
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.config import PROJECTNAME as product
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from zope.interface import alsoProvides

version = "2.4.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)


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


def reindex_qc_analyses(tool):
    """Reindex the QC analyses to ensure they are displayed again in worksheets

    :param tool: portal_setup tool
    """
    logger.info("Reindexing QC Analyses ...")
    query = {
        "portal_type": ["DuplicateAnalysis", "ReferenceAnalysis"],
        "review_state": "assigned",
    }
    brains = api.search(query, ANALYSIS_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Reindexed {0}/{1} QC analyses".format(num, total))

        obj = api.get_object(brain)
        obj.reindexObject(idxs=["getWorksheetUID", "getAnalyst"])

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Reindexing QC Analyses [DONE]")


def mark_retracted_and_rejected_analyses(tool):
    """Sets the IRetracted and/or IRejected interface to analyses that were
    either retracted or rejected
    :param tool: portal_setup tool
    """
    logger.info("Set IRetracted/IRejected interface to analyses ...")
    query = {
        "portal_type": ["Analysis", "ReferenceAnalysis", "DuplicateAnalysis"],
        "review_state": ["retracted", "rejected"],
    }
    brains = api.search(query, ANALYSIS_CATALOG)
    total = len(brains)

    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Set IRetracted/IRejected {0}/{1}".format(num, total))

        obj = api.get_object(brain)
        if IRetracted.providedBy(obj):
            obj._p_deactivate()  # noqa
            continue

        if IRejected.providedBy(obj):
            obj._p_deactivate()  # noqa
            continue

        status = api.get_review_status(obj)
        if status == "retracted":
            alsoProvides(obj, IRetracted)
        elif status == "rejected":
            alsoProvides(obj, IRejected)

    logger.info("Set IRetracted/IRejected interface to analyses [DONE]")


def fix_sample_actions_not_translated(tool):
    """Changes the name of the action item displayed in the actions list from
    sample (actbox) for the transitions 'submit' and 'receive'

    :param tool: portal_setup tool
    """
    logger.info("Fix sample actions without translation ...")
    actions = ["submit", "receive"]
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("senaite_sample_workflow")
    for action in actions:
        transition = workflow.transitions.get(action)

        # update action with title
        transition.actbox_name = transition.title

    logger.info("Fix sample actions without translation [DONE]")


def import_typeinfo(tool):
    """Import typeinfo step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile("profile-bika.lims:default", "typeinfo")
    setup.runImportStepFromProfile(profile, "typeinfo")


def fix_traceback_retract_dl(tool):
    """Migrates the values of LDL and UDL of analyses/services to string, as
    well as results that are DetectionLimit and stored as floats
    """
    logger.info("Migrate LDL, UDL and result fields to string ...")
    cat = api.get_tool("uid_catalog")
    query = {"portal_type": ["AnalysisService", "Analysis",
                             "DuplicateAnalysis", "ReferenceAnalysis"]}
    brains = cat.search(query)
    total = len(brains)

    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Migrated {0}/{1} LDL/UDL fields".format(num, total))

        if num and num % 1000 == 0:
            # reduce memory size of the transaction
            transaction.savepoint()

        obj = api.get_object(brain)

        # Migrate UDL to string
        field = obj.getField("UpperDetectionLimit")
        value = field.get(obj)
        if isinstance(value, (int, float)):
            field.set(obj, str(value))

        # Migrate LDL to string
        field = obj.getField("LowerDetectionLimit")
        value = field.get(obj)
        if isinstance(value, (int, float)):
            field.set(obj, str(value))

        # Migrate the result
        field = obj.getField("Result")
        if field and obj.getDetectionLimitOperand() in [LDL, UDL]:
            # The result is the detection limit
            result = field.get(obj)
            if isinstance(result, (int, float)):
                field.set(obj, str(result))

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Migrate LDL, UDL and result fields to string [DONE]")


def purge_computed_fields_profile(self):
    """Cleanup of computed fields related with Profiles field and removal of
    indexes and columns that are no longer required
    """
    logger.info("Purge ComputedField from Sample related with Profiles ...")
    indexes_to_remove = [
    ]
    columns_to_remove = [
        ("getProfilesUID", SAMPLE_CATALOG),
        ("getProfilesURL", SAMPLE_CATALOG),
        ("getProfilesTitle", SAMPLE_CATALOG),
    ]

    # Purge the catalogs
    purge_catalogs(indexes_to_remove, columns_to_remove)

    logger.info("Purge ComputedField from Sample related with Profiles [DONE]")


def purge_catalogs(indexes_to_remove, columns_to_remove):
    """Removes the indexes and columns from catalogs
    """
    # remove indexes
    for index_name, catalog_id in indexes_to_remove:
        cat = api.get_tool(catalog_id)
        if index_name in cat.indexes():
            logger.info("Removing '{}' index from '{}'".format(
                index_name, catalog_id))
            cat.delIndex(index_name)

    # remove columns
    for col_name, catalog_id in columns_to_remove:
        cat = api.get_tool(catalog_id)
        if col_name in cat.schema():
            logger.info("Removing '{}' column from '{}'".format(
                col_name, catalog_id))
            cat.delColumn(col_name)


def remove_default_container_type(tool):
    """Removes references from the old "DefaultContainerType" field
    """
    ref_id = "AnalysisRequestContainerType"
    ref_tool = api.get_tool(REFERENCE_CATALOG)
    cat = api.get_tool(SAMPLE_CATALOG)
    brains = cat(portal_type="AnalysisRequest")
    total = len(brains)
    for num, sample in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Processed samples: {}/{}".format(num, total))

        if num and num % 1000 == 0:
            # reduce memory size of the transaction
            transaction.savepoint()

        # Remove AnalysisRequestContainerType references
        obj = api.get_object(sample)
        ref_tool.deleteReferences(obj, relationship=ref_id)

        # Flush the object from memory
        obj._p_deactivate()


def migrate_analysisrequest_referencefields(tool):
    """Migrates the ReferenceField from AnalysisRequest to UIDReferenceField
    """
    logger.info("Migrate ReferenceFields to UIDReferenceField ...")
    field_names = [
        "Attachment",
        "Batch",
        "CCContact",
        "Client",
        "DetachedFrom",
        "Invalidated",
        "Invoice",
        "PrimaryAnalysisRequest",
        "Profiles",
        "PublicationSpecification",
        "Specification",
        "SubGroup",
        "Template",
    ]

    cat = api.get_tool(SAMPLE_CATALOG)
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


def get_relationship_key(obj, field):
    """Returns the relationship from the given object and field, taking into
    account the names of old relationships
    """
    # (<portal_type><field_name>, old_relationship_name)
    relationships = dict([
        ("AutoImportLogInstrument", "InstrumentImportLogs"),
        ("ContactCCContact", "ContactContact"),
        ("DepartmentManager", "DepartmentLabContact"),
        ("InstrumentCalibrationWorker", "LabContactInstrumentCalibration"),
        ("InstrumentCertificationPreparator", "LabContactInstrumentCertificatePreparator"),
        ("InstrumentCertificationValidator", "LabContactInstrumentCertificateValidator"),
        ("InstrumentValidationWorker", "LabContactInstrumentValidation"),
        ("InvoiceClient", "ClientInvoice"),
        ("LabContactDepartments", "LabContactDepartment"),
        ("WorksheetTemplateService", "WorksheetTemplateAnalysisService"),
        ("WorksheetTemplateRestrictToMethod", "WorksheetTemplateMethod"),
    ])
    relationship = field.get_relationship_key(obj)
    return relationships.get(relationship, relationship)


def migrate_reference_fields(obj, field_names=None):
    """Migrates the reference fields with the names specified from the obj
    """
    ref_tool = api.get_tool(REFERENCE_CATALOG)
    if field_names is None:
        field_names = api.get_fields(obj).keys()

    for field_name in field_names:

        # Get the relationship id from field
        field = obj.getField(field_name)
        if not isinstance(field, UIDReferenceField):
            continue

        ref_id = get_relationship_key(obj, field)
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


def purge_backreferences_to(obj):
    """Removes back-references that are no longer needed that point to the
    given object
    """
    fields = api.get_fields(obj)

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
        relationship = get_relationship_key(obj, field)
        references = filter(None, references)
        for reference in references:
            refob = api.get_object(reference)
            back_storage = get_storage(refob)
            back_storage.pop(relationship, None)


def migrate_and_purge_references(tool):
    """Migrate existing references from ReferenceField that now rely on the
    UIDReferenceField
    """
    logger.info("Migrate and purge references ...")

    # Extract source UIDs from reference catalog
    ref_tool = api.get_tool(REFERENCE_CATALOG)
    uids = ref_tool.uniqueValuesFor("sourceUID")
    total = len(uids)
    for num, uid in enumerate(uids):
        if num and num % 100 == 0:
            logger.info("Processed objects: {}/{}".format(num, total))

        if num and num % 1000 == 0:
            # reduce memory size of the transaction
            transaction.savepoint()

        obj = api.get_object_by_uid(uid)

        # Migrate reference fields
        migrate_reference_fields(obj)

        # Purge no longer required back-references
        purge_backreferences_to(obj)

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Migrate and purge references [DONE]")
