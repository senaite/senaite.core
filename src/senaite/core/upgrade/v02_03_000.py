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

from bika.lims import api
from Products.Archetypes.config import REFERENCE_CATALOG
from senaite.core import logger
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import REPORT_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog.report_catalog import ReportCatalog
from senaite.core.config import PROJECTNAME as product
from senaite.core.setuphandlers import _run_import_step
from senaite.core.setuphandlers import add_senaite_setup
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils

version = "2.3.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)


METADATA_TO_REMOVE = [
    # No longer used, see https://github.com/senaite/senaite.core/pull/2025/
    (ANALYSIS_CATALOG, "getAnalyst"),
    (ANALYSIS_CATALOG, "getAnalystName"),
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

    # run import steps located in bika.lims profiles
    _run_import_step(portal, "rolemap", profile="profile-bika.lims:default")

    # run import steps located in senaite.core profiles
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "typeinfo")
    setup.runImportStepFromProfile(profile, "workflow")
    setup.runImportStepFromProfile(profile, "plone.app.registry")
    setup.runImportStepFromProfile(profile, "controlpanel")

    # Add new setup folder to portal
    add_senaite_setup(portal)

    remove_stale_metadata(portal)
    fix_samples_primary(portal)
    fix_worksheets_analyses(portal)
    fix_cannot_create_partitions(portal)
    fix_interface_interpretation_template(portal)
    fix_unassigned_samples(portal)
    move_arreports_to_report_catalog(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def fix_samples_primary(portal):
    logger.info("Fix AnalysisRequests PrimaryAnalysisRequest ...")
    ref_id = "AnalysisRequestParentAnalysisRequest"
    ref_tool = api.get_tool(REFERENCE_CATALOG)
    query = {
        "portal_type": "AnalysisRequest",
        "isRootAncestor": False
    }
    samples = api.search(query, SAMPLE_CATALOG)
    total = len(samples)
    for num, sample in enumerate(samples):
        if num and num % 10 == 0:
            logger.info("Processed samples: {}/{}".format(num, total))

        # Extract the parent(s) from this sample
        sample = api.get_object(sample)
        parents = sample.getRefs(relationship=ref_id)
        if not parents:
            # Processed already
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


def fix_cannot_create_partitions(portal):
    """Updates the role mappings of samples in status that are affected by the
    issue: sample_received, verified, to_be_verified and published statuses
    """
    logger.info("Fix cannot create partitions ...")
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("senaite_sample_workflow")
    statuses = ["sample_received", "to_be_verified", "verified", "published"]
    query = {
        "portal_type": "AnalysisRequest",
        "review_state": statuses,
    }
    brains = api.search(query, SAMPLE_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 10 == 0:
            logger.info("Fix cannot create partitions {0}/{1}".format(num, total))
        obj = api.get_object(brain)
        workflow.updateRoleMappingsFor(obj)
        obj.reindexObject(idxs=["allowedRolesAndUsers"])


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


def fix_interface_interpretation_template(portal):
    """Applies IInterpretationTempalteSchema to InterpretationTemplate FTI
    """
    logger.info("Fix interface for InterpretationTemplate FTI ...")
    pt = api.get_tool("portal_types")
    fti = pt.get("InterpretationTemplate")
    fti.schema = "senaite.core.content.interpretationtemplate.IInterpretationTemplateSchema"
    logger.info("Fix interface for InterpretationTemplate FTI ...")


def fix_unassigned_samples(portal):
    """Reindex the 'assigned_state' index for samples
    """
    logger.info("Fix unassigned samples ...")
    indexes = ["assigned_state"]
    query = {
        "portal_type": "AnalysisRequest",
        "assigned_state": "unassigned",
    }
    cat = api.get_tool(SAMPLE_CATALOG)
    samples = api.search(query, SAMPLE_CATALOG)
    total = len(samples)
    for num, sample in enumerate(samples):

        if num and num % 100 == 0:
            logger.info("Fix unassigned samples {0}/{1}".format(num, total))

        obj = api.get_object(sample)
        obj_url = api.get_path(sample)
        cat.catalog_object(obj, obj_url, idxs=indexes, update_metadata=1)

        # Flush the object from memory
        obj._p_deactivate()  # noqa

    logger.info("Fix unassigned samples ...")


def move_arreports_to_report_catalog(portal):
    """Move ARReport objects to report catalog
    """
    # Check if ARReport is already in archetype_tool mapped
    at = api.get_tool("archetype_tool")
    portal_type = "ARReport"
    report_catalog = api.get_tool(REPORT_CATALOG)
    catalogs = at.getCatalogsByType(portal_type)
    if report_catalog in catalogs:
        # we assume that the upgrade step already ran
        return

    logger.info("Move ARReports to SENAITE Report Catalog ...")
    # Ensure all new indexes are in place
    setup_core_catalogs(portal, catalog_classes=(ReportCatalog,))

    # setup catalogs
    existing_catalogs = list(map(lambda c: c.getId(), catalogs))
    new_catalogs = existing_catalogs + [REPORT_CATALOG]
    at.setCatalogsByType(portal_type, new_catalogs)

    # reindex arreports
    brains = api.search({"portal_type": portal_type}, catalog="portal_catalog")
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Reindexed {0}/{1} sample reports".format(num, total))

        obj = api.get_object(brain)
        obj.reindexObject()

        # Flush the object from memory
        obj._p_deactivate()  # noqa

    logger.info("Move ARReports to SENAITE Report Catalog [DONE]")
