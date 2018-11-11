# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.DCWorkflow.Guard import Guard
from Products.ZCatalog.ProgressHandler import ZLogHandler
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.workflow import changeWorkflowState

version = '1.3.0'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)

PORTLETS_TO_PURGE = [
    'accreditation-pt',
    'login',
    'news',
    'events',
    'Calendar',
    'portlet_department_filter-pt',
    'portlet_to_be_sampled-pt',
    'portlet_to_be_preserved-pt',
    'portlet_late_analyses-pt',
    'portlet_pending_orders-pt',
    'portlet_sample_due-pt',
    'portlet_to_be_verified-pt',
    'portlet_verified-pt'
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
    setup.runImportStepFromProfile(profile, 'typeinfo')

    # Remove QC reports and gpw dependency
    # https://github.com/senaite/senaite.core/pull/1058
    remove_qc_reports(portal)

    # Remove updates notification viewlet
    # https://github.com/senaite/senaite.core/pull/1059
    setup.runImportStepFromProfile(profile, 'viewlets')

    # Remove old portlets except the navigation portlet
    # https://github.com/senaite/senaite.core/pull/1060
    purge_portlets(portal)

    # Setup the partitioning system
    setup_partitioning(portal)

    # Fix Cannot get the allowed transitions (guard_sample_prep_transition)
    # https://github.com/senaite/senaite.core/pull/1069
    remove_sample_prep_workflow(portal)

    # Rebind calculations of active analyses. The analysis Calculation (an
    # HistoryAwareField) cannot resolve DependentServices
    # https://github.com/senaite/senaite.core/pull/1072
    rebind_calculations(portal)

    # Reindex Multifiles, so that the fields are searchable by the catalog
    # https://github.com/senaite/senaite.core/pull/1080
    reindex_multifiles(portal)

    # Reindex Clients, so that the fields are searchable by the catalog
    # https://github.com/senaite/senaite.core/pull/1080
    reindex_clients(portal)

    # Removed `not requested analyses` from AR view
    remove_not_requested_analyses_view(portal)

    # Update workflows
    update_workflows(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_qc_reports(portal):
    """Removes the action Quality Control from Reports
    """
    logger.info("Removing Reports > Quality Control ...")
    ti = portal.reports.getTypeInfo()
    actions = map(lambda action: action.id, ti._actions)
    for index, action in enumerate(actions, start=0):
        if action == 'qualitycontrol':
            ti.deleteActions([index])
            break
    logger.info("Removing Reports > Quality Control [DONE]")


def purge_portlets(portal):
    """Remove old portlets. Leave the Navigation portlet only
    """
    logger.info("Purging portlets ...")

    def remove_portlets(context_portlet):
        mapping = portal.restrictedTraverse(context_portlet)
        for key in mapping.keys():
            if key not in PORTLETS_TO_PURGE:
                logger.info("Skipping portlet: '{}'".format(key))
                continue
            logger.info("Removing portlet: '{}'".format(key))
            del mapping[key]

    remove_portlets("++contextportlets++plone.leftcolumn")
    remove_portlets("++contextportlets++plone.rightcolumn")

    # Reimport the portlets profile
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, 'portlets')
    logger.info("Purging portlets [DONE]")

def setup_partitioning(portal):
    """Setups the enhanced partitioning system
    """
    logger.info("Setting up the enhanced partitioning system")

    # Add "Create partition" transition
    add_create_partition_transition(portal)

    # Add getAncestorsUIDs index in analyses catalog
    add_partitioning_indexes(portal)

    # Adds metadata columns for partitioning
    add_partitioning_metadata(portal)


def add_create_partition_transition(portal):
    logger.info("Adding partitioning workflow")
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("bika_ar_workflow")

    # Transition: create_partitions
    update_role_mappings = False
    transition_id = "create_partitions"
    if transition_id not in workflow.transitions:
        update_role_mappings = True
        workflow.transitions.addTransition(transition_id)
    transition = workflow.transitions.create_partitions
    transition.setProperties(
        title="Create partitions",
        new_state_id='sample_received',
        after_script_name='',
        actbox_name="Create partitions", )
    guard = transition.guard or Guard()
    guard_props = {'guard_permissions': 'BIKA: Edit Results',
                   'guard_roles': '',
                   'guard_expr': 'python:here.guard_handler("create_partitions")'}
    guard.changeFromProperties(guard_props)
    transition.guard = guard

    # Add the transition to "sample_received" state
    state = workflow.states.sample_received
    if transition_id not in state.transitions:
        update_role_mappings = True
        state.transitions += (transition_id, )

    if not update_role_mappings:
        return

    # Update role mappings if necessary. Analysis Requests transitioned beyond
    # sample_received state are omitted.
    states = ["sampled", "scheduled_sampling", "to_be_preserved",
              "to_be_sampled", "sample_due", "sample_received"]
    query = dict(portal_type="AnalysisRequest", states=states)
    ars = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(ars)
    for num, ar in enumerate(ars, start=1):
        workflow.updateRoleMappingsFor(api.get_object(ar))
        if num % 100 == 0:
            logger.info("Updating role mappings: {0}/{1}".format(num, total))


def add_partitioning_indexes(portal):
    """Adds the indexes for partitioning
    """
    logger.info("Adding partitioning indexes")

    add_index(portal, catalog_id=CATALOG_ANALYSIS_LISTING,
              index_name="getAncestorsUIDs",
              index_attribute="getAncestorsUIDs",
              index_metatype="KeywordIndex")

    add_index(portal, catalog_id=CATALOG_ANALYSIS_REQUEST_LISTING,
              index_name="isRootAncestor",
              index_attribute="isRootAncestor",
              index_metatype="BooleanIndex")


def add_partitioning_metadata(portal):
    """Add metadata columns required for partitioning machinery
    """
    logger.info("Adding partitioning metadata")

    add_metadata(portal, CATALOG_ANALYSIS_REQUEST_LISTING,
                 'getRawParentAnalysisRequest')

    add_metadata(portal, CATALOG_ANALYSIS_REQUEST_LISTING,
                 "getDescendantsUIDs")


def add_index(portal, catalog_id, index_name, index_attribute, index_metatype):
    logger.info("Adding '{}' index to '{}' ...".format(index_name, catalog_id))
    catalog = api.get_tool(catalog_id)
    if index_name in catalog.indexes():
        logger.info("Index '{}' already in catalog '{}' [SKIP]"
                    .format(index_name, catalog_id))
        return
    catalog.addIndex(index_name, index_metatype)
    logger.info("Indexing new index '{}' ...".format(index_name))
    catalog.manage_reindexIndex(index_name)


def del_index(portal, catalog_id, index_name):
    logger.info("Removing '{}' index from '{}' ..."
                .format(index_name, catalog_id))
    catalog = api.get_tool(catalog_id)
    if index_name not in catalog.indexes():
        logger.info("Index '{}' not in catalog '{}' [SKIP]"
                    .format(index_name, catalog_id))
        return
    catalog.delIndex(index_name)
    logger.info("Removing old index '{}' ...".format(index_name))


def add_metadata(portal, catalog_id, column, refresh_catalog=False):
    logger.info("Adding '{}' metadata to '{}' ...".format(column, catalog_id))
    catalog = api.get_tool(catalog_id)
    if column in catalog.schema():
        logger.info("Metadata '{}' already in catalog '{}' [SKIP]"
                    .format(column, catalog_id))
        return
    catalog.addColumn(column)

    if refresh_catalog:
        logger.info("Refreshing catalog '{}' ...".format(catalog_id))
        handler = ZLogHandler(steps=100)
        catalog.refreshCatalog(pghandler=handler)


def del_metadata(portal, catalog_id, column, refresh_catalog=False):
    logger.info("Removing '{}' metadata from '{}' ..."
                .format(column, catalog_id))
    catalog = api.get_tool(catalog_id)
    if column not in catalog.schema():
        logger.info("Metadata '{}' not in catalog '{}' [SKIP]"
                    .format(column, catalog_id))
        return
    catalog.delColumn(column)

    if refresh_catalog:
        logger.info("Refreshing catalog '{}' ...".format(catalog_id))
        handler = ZLogHandler(steps=100)
        catalog.refreshCatalog(pghandler=handler)


def remove_sample_prep_workflow(portal):
    """Removes sample_prep and sample_prep_complete transitions
    """
    # There is no need to walk through objects because of:
    # https://github.com/senaite/senaite.core/blob/master/bika/lims/upgrade/v01_02_008.py#L187
    logger.info("Removing 'sample_prep' related states and transitions ...")
    workflow_ids = ["bika_sample_workflow",
                    "bika_ar_workflow",
                    "bika_analysis_workflow"]
    to_remove = ["sample_prep", "sample_prep_complete"]
    wf_tool = api.get_tool("portal_workflow")
    for wf_id in workflow_ids:
        workflow = wf_tool.getWorkflowById(wf_id)
        for state_trans in to_remove:
            if state_trans in workflow.transitions:
                logger.info("Removing transition '{}' from '{}'"
                            .format(state_trans, wf_id))
                workflow.transitions.deleteTransitions([state_trans])
            if state_trans in workflow.states:
                logger.info("Removing state '{}' from '{}'"
                            .format(state_trans, wf_id))
                workflow.states.deleteStates([state_trans])


def rebind_calculations(portal):
    """Rebind calculations of active analyses. The analysis Calculation (an
    HistoryAwareField) cannot resolve DependentServices"""
    logger.info("Rebinding calculations to analyses ...")
    review_states = ["sample_due",
                     "attachment_due",
                     "sample_received",
                     "to_be_verified"]

    calcs = {}
    brains = api.search(dict(portal_type="Calculation"), "bika_setup_catalog")
    for calc in brains:
        calc = api.get_object(calc)
        calc.setFormula(calc.getFormula())
        calcs[api.get_uid(calc)] = calc

    query = dict(review_state=review_states)
    analyses = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(analyses)
    for num, analysis in enumerate(analyses):
        if num % 100 == 0:
            logger.info("Rebinding calculations to analyses: {0}/{1}"
                        .format(num, total))
        analysis = api.get_object(analysis)
        calc = analysis.getCalculation()
        if not calc:
            continue

        calc_uid = api.get_uid(calc)
        if calc_uid not in calcs:
            logger.warn("Calculation with UID {} not found!".format(calc_uid))
            continue

        calc = calcs[calc_uid]
        an_interims = analysis.getInterimFields()
        an_interims_keys = map(lambda interim: interim.get('keyword'),
                               an_interims)
        calc_interims = filter(lambda interim: interim.get('keyword')
                                            not in an_interims_keys,
                            calc.getInterimFields())
        analysis.setCalculation(calc)
        analysis.setInterimFields(an_interims + calc_interims)


def reindex_multifiles(portal):
    """Reindex Multifiles to be searchable by the catalog
    """
    logger.info("Reindexing Multifiles ...")

    brains = api.search(dict(portal_type="Multifile"), "bika_setup_catalog")
    total = len(brains)

    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Reindexing Multifile: {0}/{1}".format(num, total))
        obj = api.get_object(brain)
        obj.reindexObject()


def reindex_clients(portal):
    """Reindex Clients to be searchable by their ClientName
    """
    logger.info("Reindexing Clients ...")

    brains = api.search(dict(portal_type="Client"), "portal_catalog")
    total = len(brains)

    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Reindexing Client: {0}/{1}".format(num, total))
        obj = api.get_object(brain)
        obj.reindexObject()


def remove_not_requested_analyses_view(portal):
    """Remove the view 'Not requested analyses" from inside AR
    """
    logger.info("Removing 'Analyses not requested' view ...")
    ar_ptype = portal.portal_types.AnalysisRequest
    ar_ptype._actions = filter(lambda act: act.id != "analyses_not_requested",
                               ar_ptype.listActions())


def update_workflows(portal):
    logger.info("Updating workflows ...")

    # IMPORTANT: The order of function calls is important!

    # Need to know first for which workflows we'll need later to update role
    # mappings. This will allow us to update role mappings for those required
    # objects instead of all them. I know, would be easier to just do all them,
    # but we cannot afford such an approach for huge databases
    rm_queries = get_role_mappings_candidates(portal)

    # Remove duplicates not assigned to any worksheet
    remove_orphan_duplicates(profile)

    # Remove reference analyses not assigned to any worksheet or instrument
    remove_orphan_reference_analyses(profile)

    # Re-import workflow tool
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, 'workflow')

    # Fix analyses stuck in sample* states
    decouple_analyses_from_sample_workflow(portal)

    # Remove worksheet_analysis workflow
    remove_worksheet_analysis_workflow(portal)

    # Update role mappings
    update_role_mappings(portal, rm_queries)


def remove_orphan_duplicates(portal):
    logger.info("Removing orphan duplicates ...")
    query = dict(portal_type="DuplicateAnalysis")
    brains = filter(lambda dup: not dup.getWorksheetUID,
                  api.search(query, CATALOG_ANALYSIS_LISTING))
    total = len(brains)
    for num, brain in enumerate(brains):
        orphan = api.get_object(brain)
        worksheet = orphan.getWorksheet()
        if worksheet:
            # This one has a worksheet! reindex and do nothing
            orphan.reindexObject()
            total -= 1
            continue

        if num % 100 == 0:
            logger.info("Removing orphan duplicate: {}/{}"
                        .format(num, total))
        # Remove the duplicate
        worksheet.manage_delObjects(orphan.getId())


def remove_orphan_reference_analyses(portal):
    logger.info("Removing orphan reference analyses ...")
    query = dict(portal_type="ReferenceAnalysis")
    brains = filter(lambda ref: not ref.getWorksheetUID,
                    api.search(query, CATALOG_ANALYSIS_LISTING))
    total = len(brains)
    for num, brain in enumerate(brains):
        orphan = api.get_object(brain)
        worksheet = orphan.getWorksheet()
        if worksheet:
            # This one has a worksheet! reindex and do nothing
            orphan.reindexObject()
            total -= 1
            continue
        elif orphan.getInstrument():
            # This is an calibration test, do nothing!
            if not brain.getInstrumentUID:
                orphan.reindexObject()
            total -= 1
            continue

        if num % 100 == 0:
            logger.info("Removing orphan reference analysis: {}/{}"
                        .format(num, total))
        # Remove the duplicate
        orphan.aq_parent.manage_delObjects(orphan.getId())


def get_role_mappings_candidates(portal):
    logger.info("Getting candidates for role mappings ...")

    candidates = list()
    wf_tool = api.get_tool("portal_workflow")

    # Analysis workflow
    workflow = wf_tool.getWorkflowById("bika_analysis_workflow")
    if "BIKA: Verify" not in workflow.states.to_be_verified.permissions:
        candidates.append(
            ("bika_analysis_workflow",
             dict(portal_type="Analysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Analysis workflow: multi-verify transition
    if "multi_verify" not in workflow.transitions:
        candidates.append(
            ("bika_analysis_workflow",
             dict(portal_type="Analysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Duplicate Analysis Workflow
    workflow = wf_tool.getWorkflowById("bika_duplicateanalysis_workflow")
    if "BIKA: Verify" not in workflow.states.to_be_verified.permissions:
        candidates.append(
            ("bika_duplicateanalysis_workflow",
             dict(portal_type="DuplicateAnalysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Duplicate Analysis Workflow: unasssigned
    if "unassigned" in workflow.states:
        candidates.append(
            ("bika_duplicateanalysis_workflow",
             dict(portal_type="DuplicateAnalysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Duplicate Analysis workflow: multi-verify transition
    if "multi_verify" not in workflow.transitions:
        candidates.append(
            ("bika_analysis_workflow",
             dict(portal_type="Analysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Reference Analysis Workflow
    workflow = wf_tool.getWorkflowById("bika_referenceanalysis_workflow")
    if "BIKA: Verify" not in workflow.states.to_be_verified.permissions:
        candidates.append(
            ("bika_referenceanalysis_workflow",
             dict(portal_type="ReferenceAnalysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Refernce Analysis workflow: multi-verify transition
    if "multi_verify" not in workflow.transitions:
        candidates.append(
            ("bika_analysis_workflow",
             dict(portal_type="Analysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Reference Analysis Workflow: unasssigned
    if "unassigned" in workflow.states:
        candidates.append(
            ("bika_duplicateanalysis_workflow",
             dict(portal_type="DuplicateAnalysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    return candidates


def decouple_analyses_from_sample_workflow(portal):
    logger.info("Decoupling analyses from sample workflow ...")

    add_index(portal, catalog_id=CATALOG_ANALYSIS_LISTING,
              index_name="isSampleReceived",
              index_attribute="isSampleReceived",
              index_metatype="BooleanIndex")

    wf_id = "bika_analysis_workflow"
    affected_rs = ["sample_registered", "to_be_sampled", "sampled",
                   "sample_due", "sample_received", "to_be_preserved",
                   "not_requested", "registered"]
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    query = dict(portal_type=["Analysis" "DuplicateAnalysis"],
                 review_state=affected_rs)
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        # Set state
        analysis = api.get_object(brain)
        target_state = analysis.getWorksheet() and "assigned" or "unassigned"

        if num % 100 == 0:
            logger.info("Restoring state to '{}': {}/{}"
                        .format(target_state, num, total))

        changeWorkflowState(analysis, wf_id, target_state)

        # Update role mappings
        workflow.updateRoleMappingsFor(analysis)

        # Reindex
        analysis.reindexObject()


def remove_worksheet_analysis_workflow(portal):
    logger.info("Purging worksheet analysis workflow residues ...")

    del_metadata(portal, catalog_id=CATALOG_ANALYSIS_LISTING,
                 column="worksheetanalysis_review_state",
                 refresh_catalog=False)

    del_index(portal, catalog_id=CATALOG_ANALYSIS_LISTING,
              index_name="worksheetanalysis_review_state")


def update_role_mappings(portal, queries):
    logger.info("Updating role mappings ...")
    processed = dict()
    for rm_query in queries:
        wf_tool = api.get_tool("portal_workflow")
        wf_id = rm_query[0]
        workflow = wf_tool.getWorkflowById(wf_id)
        brains = api.search(rm_query[1], rm_query[2])
        total = len(brains)
        for num, brain in enumerate(brains):
            if num % 100 == 0:
                logger.info("Updating role mappings '{0}': {1}/{2}"
                            .format(wf_id, num, total))
            if api.get_uid(brain) in processed.get(wf_id, []):
                # Already processed, skip
                continue
            workflow.updateRoleMappingsFor(api.get_object(brain))
            if wf_id not in processed:
                processed[wf_id] = []
            processed[wf_id].append(api.get_uid(brain))
