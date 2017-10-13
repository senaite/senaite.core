# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from bika.lims import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.utils import changeWorkflowState
from bika.lims.workflow import getCurrentState
from bika.lims.workflow import wasTransitionPerformed
from plone.api.portal import get_tool

product = 'bika.lims'
version = '3.2.0.1706'


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    ut = UpgradeUtils(portal)
    ufrom = ut.getInstalledVersion(product)
    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ufrom, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ufrom, version))

    # Updating lims catalogs if there is any change in them
    logger.info("Updating catalogs...")
    change_UUIDIndex(ut)
    ut.refreshCatalogs()
    logger.info("Catalogs updated")

    # Fix ARs - Analyses in inconsistent state
    # Transitioning Analysis Requests that were created before the upgrade
    # step 17.05 to "received" state, their analyses remain in "sample_due"
    # state. The analyses are therefore not available for assigning to
    # worksheets or entering results.
    # Note that after this issue happened, updateRoleMappings was added in
    # v3.2.0.17.05 upgrade step as a safeguard. The fix in this upgrade should
    # only work in those instances that were upgraded to 3.2.0.17.05 before
    # updateRoleMappings was added (see commit 0931858)
    fix_ar_analyses_statuses_inconsistences(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def fix_ar_analyses_statuses_inconsistences(portal):
    logger.info("Fixing Analysis Request-Analyses statuses inconsistences...")

    # Walkthrough 'received' analysis requests and find inconsistences:
    # If Analysis Request's state is 'received', then:
    # - Sample must be in received state too
    # - Sample Partitions must be in received state too
    # - Analyses must be in received state too
    target_state = 'sample_received'
    catalog = get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    brains = catalog(portal_type='AnalysisRequest', review_state=target_state)
    for brain in brains:
        analysisrequest = brain.getObject()
        # Check Sample
        sample = analysisrequest.getSample()
        if sample:
            sample_state = getCurrentState(sample)
            if sample_state != target_state:
                if not wasTransitionPerformed(sample, 'receive'):
                    # Do force the state to received
                    logger.info("{0}: '{1}' ({2}) -> {3}".format(
                        'Sample', sample.getId(), sample_state, target_state))
                    changeWorkflowState(sample, 'bika_sample_workflow',
                                        target_state)

            # Check Sample partitions
            parts = sample.objectValues('SamplePartition')
            for part in parts:
                part_state = getCurrentState(part)
                if part_state != target_state:
                    if not wasTransitionPerformed(part, 'receive'):
                        # Do force the state to received
                        logger.info("{0}: '{1}' ({2}) -> {3}".format(
                            'SamplePartition', part.getId(), part_state,
                            target_state))
                        changeWorkflowState(part, 'bika_sample_workflow',
                                            target_state)

        # Check analyses
        analyses = analysisrequest.getAnalyses(full_objects=True)
        for analysis in analyses:
            an_state = getCurrentState(analysis)
            if an_state != target_state:
                if not wasTransitionPerformed(analysis, 'receive'):
                    # Do force the state to received
                    logger.info("{0}: '{1}' ({2}) -> {3}".format(
                        'Analysis', analysis.getId(), an_state, target_state))
                    changeWorkflowState(analysis, 'bika_analysis_workflow',
                                        target_state)

    # Force the update of role mappings
    logger.info("Updating role mappings...")
    wf = get_tool('portal_workflow')
    wf.updateRoleMappings()


def change_UUIDIndex(ut):
    """
    UUIDIndex behaves like a FieldIndex, but can only store one document id
    per value, so there's a 1:1 mapping from value to document id. An error
    is logged if a different document id is indexed for an already taken value.

    Some UUIDIndexes need to be migrated to FieldIndexes because more than one
    field could contain the same UID, for instance
    getOriginalReflexedAnalysisUID field.
    """
    ut.delIndex(CATALOG_ANALYSIS_LISTING, 'getOriginalReflexedAnalysisUID')
    ut.addIndex(
        CATALOG_ANALYSIS_LISTING,
        'getOriginalReflexedAnalysisUID',
        'FieldIndex'
        )
