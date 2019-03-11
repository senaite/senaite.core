# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import time

import transaction
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog.worksheet_catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.interfaces import IAnalysisRequestPartition
from bika.lims.interfaces import IAnalysisRequestRetest
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.interfaces import INumberGenerator
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.permissions import TransitionVerify
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.workflow import ActionHandlerPool
from bika.lims.workflow import changeWorkflowState
from bika.lims.workflow import doActionFor as do_action_for
from bika.lims.workflow import isTransitionAllowed
from bika.lims.workflow.analysis.events import reindex_request
from bika.lims.workflow.analysis.events import remove_analysis_from_worksheet
from Products.DCWorkflow.Guard import Guard
from Products.ZCatalog.ProgressHandler import ZLogHandler
from zope.component import getUtility
from zope.interface import alsoProvides
from Products.ZCatalog.interfaces import IZCatalog
from Products.CMFCore.interfaces import ICatalogTool

version = '1.3.0'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)

PROXY_FIELDS_TO_PURGE = [
    "ClientReference",
    "ClientSampleID",
    "Composite",
    "DateReceived",
    "DateSampled",
    "EnvironmentalConditions",
    "SampleCondition",
    "SamplePoint",
    "SampleType",
    "Sampler",
    "SamplingDate",
    "SamplingDeviation",
    "ScheduledSamplingSampler",
    "StorageLocation",
]

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

JAVASCRIPTS_TO_REMOVE = [
    "++resource++bika.lims.js/bika.lims.sample.js",
    "++resource++bika.lims.js/bika.lims.samples.js",
    "++resource++bika.lims.js/bika.lims.samples.print.js",
    "++resource++bika.lims.js/bika.lims.utils.calcs.js",
    "++resource++bika.lims.js/bika.lims.analysisrequest.publish.js",
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
    setup.runImportStepFromProfile(profile, 'content')

    # Notify on AR Retraction --> Notify on Sample Invalidation
    # https://github.com/senaite/senaite.core/pull/1244
    update_notify_on_sample_invalidation(portal)

    # Remove stale indexes from bika_catalog
    # https://github.com/senaite/senaite.core/pull/1180
    remove_stale_indexes_from_bika_catalog(portal)

    # Remove stale javascripts
    # https://github.com/senaite/senaite.core/pull/1180
    remove_stale_javascripts(portal)

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

    # Port Analysis Request Proxy Fields
    # https://github.com/senaite/senaite.core/pull/1180
    port_analysis_request_proxy_fields(portal)

    # Change ID Formatting of Analysis Request to {sampleType}-{seq:04d}
    # https://github.com/senaite/senaite.core/pull/1180
    change_analysis_requests_id_formatting(portal)

    # Add catalog indexes for reference sample handling in Worksheets
    # https://github.com/senaite/senaite.core/pull/1091
    add_reference_sample_indexes(portal)

    # Removed `not requested analyses` from AR view
    remove_not_requested_analyses_view(portal)

    # Remove getDepartmentUID indexes + metadata
    # https://github.com/senaite/senaite.core/pull/1167
    remove_get_department_uids(portal)

    # Update workflows
    update_workflows(portal)

    # Add catalog indexes needed for worksheets
    # https://github.com/senaite/senaite.core/pull/1114
    add_worksheet_indexes(portal)

    # https://github.com/senaite/senaite.core/pull/1118
    remove_bika_listing_resources(portal)

    # Remove samples views from everywhere (navbar, client, batches, etc.)
    # https://github.com/senaite/senaite.core/pull/1125
    hide_samples(portal)

    # Fix Calculation versioning inconsistencies
    # https://github.com/senaite/senaite.core/pull/1260
    fix_calculation_version_inconsistencies(portal)

    # Fix Analysis Request - Analyses inconsistencies
    # https://github.com/senaite/senaite.core/pull/1138
    fix_ar_analyses_inconsistencies(portal)

    # Add getProgressPercentage metadata for worksheets
    # https://github.com/senaite/senaite.core/pull/1153
    add_worksheet_progress_percentage(portal)

    # Worksheet can only be open if at least one analysis hasn't been verified
    # https://github.com/senaite/senaite.core/pull/1191
    fix_worksheet_status_inconsistencies(portal)

    # Replaces Analysis Request string (and plural forms) by Sample
    rename_analysis_requests_actions(portal)

    # Apply IAnalysisRequestPartition marker interface to preexisting partitions
    apply_analysis_request_partition_interface(portal)

    # Updates Indexes/Metadata of bika_catalog_analysisrequest_listing
    # https://github.com/senaite/senaite.core/pull/1230
    update_ar_listing_catalog(portal)

    # Updates Indexes/Metadata of the bika_catalog
    # https://github.com/senaite/senaite.core/pull/1231
    update_bika_catalog(portal)

    # Updates Indexes/Metadata of the bika_analysis_catalog
    # https://github.com/senaite/senaite.core/pull/1227
    update_bika_analysis_catalog(portal)

    # Updates Indexes/Metadata of the bika_catalog_worksheet_listing
    # https://github.com/senaite/senaite.core/pull/1227
    update_bika_catalog_worksheet_listing(portal)

    # Updates Indexes/Metadata of the bika_setup_catalog
    # https://github.com/senaite/senaite.core/pull/1227
    update_bika_setup_catalog(portal)

    # Updates Indexes/Metadata of the bika_catalog_report
    # https://github.com/senaite/senaite.core/pull/1227
    update_bika_catalog_report(portal)

    # Updates Indexes/Metadata of the portal_catalog
    # https://github.com/senaite/senaite.core/pull/1227
    update_portal_catalog(portal)

    # Apply IAnalysisRequestRetest marker interface to retested ARs
    # https://github.com/senaite/senaite.core/pull/1243
    apply_analysis_request_retest_interface(portal)

    # Set the ID formatting for AR restest
    # https://github.com/senaite/senaite.core/pull/1243
    set_retest_id_formatting(portal)

    # Reindex submitted analyses to update the analyst
    # https://github.com/senaite/senaite.core/pull/1254
    reindex_submitted_analyses(portal)

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

    # Setup default ID formatting for partitions
    set_partitions_id_formatting(portal)


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
    guard_props = {'guard_permissions': 'senaite.core: Edit Results',
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


def add_reference_sample_indexes(portal):
    """Adds the indexes for partitioning
    """
    logger.info("Adding reference sample indexes")

    add_index(portal, catalog_id="bika_catalog",
              index_name="getSupportedServices",
              index_attribute="getSupportedServices",
              index_metatype="KeywordIndex")

    add_index(portal, catalog_id="bika_catalog",
              index_name="getBlank",
              index_attribute="getBlank",
              index_metatype="BooleanIndex")

    add_index(portal, catalog_id="bika_catalog",
              index_name="isValid",
              index_attribute="isValid",
              index_metatype="BooleanIndex")


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
    # The following is going to be highly consuming tasks, so better to first
    # do a transaction commit to free as much resources as possible
    commit_transaction(portal)

    # Need to know first for which workflows we'll need later to update role
    # mappings. This will allow us to update role mappings for those required
    # objects instead of all them. I know, would be easier to just do all them,
    # but we cannot afford such an approach for huge databases
    # UPDATE:
    # We don't use role_mappings_candidates anymore because we've changed
    # security settings for most objects and also the workflows they are bound
    # to new workflows: https://github.com/senaite/senaite.core/pull/1227
    # rm_queries = get_role_mappings_candidates(portal)

    # Assign retracted analyses to retests
    assign_retracted_to_retests(portal)

    # Remove rejected duplicates
    remove_rejected_duplicates(portal)

    # Re-import rolemap and workflow tools
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, 'rolemap')
    setup.runImportStepFromProfile(profile, 'workflow')

    # Remove duplicates not assigned to any worksheet
    remove_orphan_duplicates(portal)

    # Remove reference analyses not assigned to any worksheet or instrument
    remove_orphan_reference_analyses(portal)

    # Fix analyses stuck in sample* states
    decouple_analyses_from_sample_workflow(portal)

    # Change workflow state of analyses in attachment_due
    remove_attachment_due_from_analysis_workflow(portal)

    # Remove worksheet_analysis workflow
    remove_worksheet_analysis_workflow(portal)

    # Fix cancelled analyses inconsistencies
    # Superseded by resolve_cancellation_inactive_state(portal)
    #fix_cancelled_analyses_inconsistencies(portal)

    # Fix cancelled/inactive objects inconsistencies
    # https://github.com/senaite/senaite.core/pull/1227
    resolve_cancellation_inactive_inconsistencies(portal)

    # Decouple analysis requests from samples
    decouple_analysisrequests_from_sample(portal)

    # Fix cancelled analyses inconsistencies
    # Superseded by resolve_cancellation_inactive_state(portal)
    #decouple_analysis_requests_from_cancellation_workflow(portal)

    # Fix Analysis Requests in sampled status
    fix_analysisrequests_in_sampled_status(portal)

    # Update role mappings
    # UPDATE:
    # We do a full rolemappings update because we've changed security settings
    # for most objects and also the workflows they are bound to new workflows:
    # https://github.com/senaite/senaite.core/pull/1227
    # update_role_mappings(portal, rm_queries)
    commit_transaction(portal)
    # Recursively update the role mappings starting from the portal object
    logger.info("Recursively update role mappings ...")
    ut = UpgradeUtils(portal)
    ut.recursiveUpdateRoleMappings(portal)

    # Rollback to receive inconsistent ARs
    rollback_to_receive_inconsistent_ars(portal)
    commit_transaction(portal)


def remove_orphan_duplicates(portal):
    logger.info("Removing orphan duplicates ...")
    wf_id = "bika_duplicateanalysis_workflow"
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    query = dict(portal_type="DuplicateAnalysis",
                 review_state="unassigned")
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        orphan = api.get_object(brain)
        worksheet = orphan.getWorksheet()
        if worksheet:
            logger.info("Reassigning orphan duplicate: {}/{}"
                        .format(num, total))
            # This one has a worksheet! reindex and do nothing
            changeWorkflowState(orphan, wf_id, "assigned")
            # Update role mappings
            workflow.updateRoleMappingsFor(orphan)
            # Reindex
            orphan.reindexObject()
            continue

        if num % 100 == 0:
            logger.info("Removing orphan duplicate: {}/{}"
                        .format(num, total))
        # Remove the duplicate
        orphan.aq_parent.manage_delObjects([orphan.getId()])


def remove_rejected_duplicates(portal):
    logger.info("Removing rejected duplicates ...")
    query = dict(portal_type="DuplicateAnalysis",
                 review_state="rejected")
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Removing rejected duplicate: {}/{}"
                        .format(num, total))
        orphan = api.get_object(brain)
        worksheet = orphan.getWorksheet()
        if worksheet:
            # Remove from the worksheet first
            analyses = filter(lambda an: an != orphan, worksheet.getAnalyses())
            worksheet.setAnalyses(analyses)
            worksheet.purgeLayout()

        # Remove the duplicate
        orphan.aq_parent.manage_delObjects([orphan.getId()])
    commit_transaction(portal)


def remove_orphan_reference_analyses(portal):
    logger.info("Removing orphan reference analyses ...")
    wf_id = "bika_referenceanalysis_workflow"
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    query = dict(portal_type="ReferenceAnalysis",
                 review_state="unassigned")
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        orphan = api.get_object(brain)
        worksheet = orphan.getWorksheet()
        if worksheet:
            logger.info("Reassigning orphan reference: {}/{}"
                        .format(num, total))
            # This one has a worksheet! reindex and do nothing
            changeWorkflowState(orphan, wf_id, "assigned")
            # Update role mappings
            workflow.updateRoleMappingsFor(orphan)
            # Reindex
            orphan.reindexObject()
            continue
        elif orphan.getInstrument():
            # This is a calibration test, do nothing!
            if not brain.getInstrumentUID:
                orphan.reindexObject()
            total -= 1
            continue

        if num % 100 == 0:
            logger.info("Removing orphan reference analysis: {}/{}"
                        .format(num, total))
        # Remove the duplicate
        orphan.aq_parent.manage_delObjects([orphan.getId()])


def assign_retracted_to_retests(portal):
    logger.info("Reassigning retracted to retests ...")
    # Note this is confusing, getRetested index tells us if the analysis is a
    # retest, not the other way round! (the analysis has been retested)
    catalog = api.get_tool(CATALOG_ANALYSIS_LISTING)
    if "getRetested" not in catalog.indexes():
        return

    processed = list()
    query = dict(getRetested="True")
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        retest = api.get_object(brain)
        retest_uid = api.get_uid(retest)
        if retest.getRetestOf():
            # We've been resolved this inconsistency already
            total -= 1
            continue
        # Look for the retest
        if IDuplicateAnalysis.providedBy(retest):
            worksheet = retest.getWorksheet()
            if not worksheet:
                total -= 1
                continue
            for dup in worksheet.get_duplicates_for(retest.getAnalysis()):
                if api.get_uid(dup) != retest_uid \
                        and api.get_workflow_status_of(dup) == "retracted":
                    retest.setRetestOf(dup)
                    processed.append(retest)
                    break
        elif IReferenceAnalysis.providedBy(retest):
            worksheet = retest.getWorksheet()
            if not worksheet:
                total -= 1
                continue
            ref_type = retest.getReferenceType()
            slot = worksheet.get_slot_position(retest.getSample(), ref_type)
            for ref in worksheet.get_analyses_at(slot):
                if api.get_uid(ref) != retest_uid \
                        and api.get_workflow_status_of(ref) == "retracted":
                    retest.setRetestOf(ref)
                    processed.append(retest)
                    break
        else:
            request = retest.getRequest()
            keyword = retest.getKeyword()
            analyses = request.getAnalyses(review_state="retracted",
                                           getKeyword=keyword)
            if not analyses:
                total -= 1
                continue
            retest.setRetestOf(analyses[-1])
            processed.append(retest)

        if num % 100 == 0:
            logger.info("Reassigning retracted analysis: {}/{}"
                        .format(num, total))

    del_metadata(portal, catalog_id=CATALOG_ANALYSIS_LISTING,
                 column="getRetested")

    add_metadata(portal, catalog_id=CATALOG_ANALYSIS_LISTING,
                 column="getRetestOfUID")

    del_index(portal, catalog_id=CATALOG_ANALYSIS_LISTING,
              index_name="getRetested")

    add_index(portal, catalog_id=CATALOG_ANALYSIS_LISTING,
              index_name="isRetest",
              index_attribute="isRetest",
              index_metatype="BooleanIndex")

    total = len(processed)
    for num, analysis in enumerate(processed):
        if num % 100 == 0:
            logger.info("Reindexing retests: {}/{}"
                        .format(num, total))
        analysis.reindexObject(idxs="isRetest")
    commit_transaction(portal)


def fix_cancelled_analyses_inconsistencies(portal):
    logger.info("Resolving cancelled analyses inconsistencies ...")
    wf_id = "bika_analysis_workflow"
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    query = dict(portal_type="Analysis", cancellation_state="cancelled")
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if brain.review_state == "cancelled":
            continue
        if num % 100 == 0:
            logger.info("Resolving state to 'cancelled': {}/{}"
                        .format(num, total))
        # Set state
        analysis = api.get_object(brain)
        changeWorkflowState(analysis, wf_id, "cancelled")
        # Update role mappings
        workflow.updateRoleMappingsFor(analysis)
        # Reindex
        analysis.reindexObject(idxs=["review_state", "is_active"])


def get_catalogs(portal):
    """Returns the catalogs from the site
    """
    res = []
    for object in portal.objectValues():
        if ICatalogTool.providedBy(object):
            res.append(object)
        elif IZCatalog.providedBy(object):
            res.append(object)
    res.sort()
    return res


def resolve_cancellation_inactive_inconsistencies(portal):
    resolve_inconsistencies_for_state(portal, "cancellation_state", "cancelled")
    resolve_inconsistencies_for_state(portal, "inactive_state", "inactive")


def resolve_inconsistencies_for_state(portal, state_idx, state_id):
    logger.info("Resolving inconsistencies for {} state ...".format(state_id))
    queries = []
    for catalog in get_catalogs(portal):
        if not catalog.Indexes.get(state_idx, None):
            continue
        catalog_id = catalog.getId()
        queries.append(({state_idx: state_id}, catalog_id))

    processed = []
    for query in queries:
        logger.info("Resolving '{}' state from '{}' ...".format(state_idx,
                                                                query[1]))
        brains = api.search(query[0], query[1])
        total = len(brains)
        for num, brain in enumerate(brains):
            if num % 100 == 0:
                logger.info("Resolving state to '{}': {}/{}".format(state_id,
                                                                    num, total))
            if api.get_uid(brain) in processed:
                continue
            if brain.review_state == state_id:
                if api.get_review_status(api.get_object(brain)) == state_id:
                    continue

            # Set state
            pt = api.get_portal_type(brain)
            workflows = api.get_workflows_for(brain)
            if not workflows:
                logger.error("No workflows found for {}".format(pt))
                continue
            elif len(workflows) > 1:
                logger.error("More than one workflow found for {}".format(pt))
                continue

            wf_id = workflows[0]
            wf_tool = api.get_tool("portal_workflow")
            workflow = wf_tool.getWorkflowById(wf_id)

            if state_id not in workflow.states:
                logger.error("'{}' state not found for {}".format(state_id,
                                                                  wf_id))

            obj = api.get_object(brain)
            if changeWorkflowState(obj, wf_id, state_id):
                processed.append(api.get_uid(obj))

            if num % 1000 == 0:
                commit_transaction(portal)

    # Remove indexes and metadata
    catalogs = map(lambda cat: cat[1], queries)
    catalogs = list(set(catalogs))
    for catalog_id in catalogs:
        del_index(portal, catalog_id=catalog_id, index_name=state_idx)
        del_metadata(portal, catalog_id=catalog_id, column=state_idx)
        add_index(portal, catalog_id=catalog_id, index_name="is_active",
                  index_attribute="is_active", index_metatype="BooleanIndex")

    commit_transaction(portal)


def get_role_mappings_candidates(portal):
    logger.info("Getting candidates for role mappings ...")
    candidates = list()
    # Analysis workflow
    candidates.extend(get_rm_candidates_for_analysisworkfklow(portal))
    # Duplicate analysis workflow
    candidates.extend(get_rm_candidates_for_duplicateanalysisworkflow(portal))
    # Reference Analysis Workflow
    candidates.extend(get_rm_candidates_for_referenceanalysisworkflow(portal))
    # Analysis Request workflow
    candidates.extend(get_rm_candidates_for_ar_workflow(portal))
    # Worksheet workflow
    candidates.extend(get_rm_candidates_for_worksheet_workflow(portal))

    return candidates


def get_workflow_by_id(portal, workflow_id):
    wf_tool = api.get_tool("portal_workflow")
    return wf_tool.getWorkflowById(workflow_id)


def get_rm_candidates_for_worksheet_workflow(portal):
    wf_id = "bika_worksheet_workflow"
    logger.info("Getting candidates for role mappings: {} ...".format(wf_id))
    workflow = get_workflow_by_id(portal, wf_id)
    candidates = list()
    if "rollback_to_open" not in workflow.transitions:
        candidates.append(
            ("bika_worksheet_workflow",
             dict(portal_type="Worksheet",
                  review_state=["to_be_verified"]),
             CATALOG_WORKSHEET_LISTING))

    if "retract" not in workflow.states.verified.transitions:
        candidates.append(
            (wf_id,
             dict(portal_type="Worksheet",
                  review_state=["attachment_due", "to_be_verified",
                                "verified"]),
             CATALOG_WORKSHEET_LISTING)
        )
    return candidates


def get_rm_candidates_for_ar_workflow(portal):
    wf_id = "bika_ar_workflow"
    logger.info("Getting candidates for role mappings: {} ...".format(wf_id))
    workflow = get_workflow_by_id(portal, wf_id)
    candidates = list()

    if workflow.title != "Sample Workflow":
        # "Bika AR Workflow" will become "Sample Workflow" after the profile
        # step "workflow" is run.
        # Since we've introduced field-specific permissions in ar_workflow, and
        # we've changed the whole rolemap.xml there is no choice: we are forced
        # to do a role mappings for all ARs :(
        candidates.append(
            (wf_id,
             dict(portal_type="AnalysisRequest"),
             CATALOG_ANALYSIS_REQUEST_LISTING))

    return candidates


def get_rm_candidates_for_referenceanalysisworkflow(portal):
    wf_id = "bika_referenceanalysis_workflow"
    logger.info("Getting candidates for role mappings: {} ...".format(wf_id))
    workflow = get_workflow_by_id(portal, wf_id)
    candidates = list()
    if TransitionVerify not in workflow.states.to_be_verified.permissions:
        candidates.append(
            (wf_id,
             dict(portal_type="ReferenceAnalysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Reference Analysis workflow: multi-verify transition
    if "multi_verify" not in workflow.transitions:
        candidates.append(
            (wf_id,
             dict(portal_type="ReferenceAnalysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Reference Analysis Workflow: unasssigned
    if "unassigned" in workflow.states:
        candidates.append(
            (wf_id,
             dict(portal_type="ReferenceAnalysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # "Modify portal content" for "assigned"
    if "Modify portal content" not in workflow.states.assigned.permissions:
        candidates.append(
            (wf_id,
             dict(portal_type="ReferenceAnalysis",
                  review_state=["assigned"]),
             CATALOG_ANALYSIS_LISTING))
    return candidates


def get_rm_candidates_for_duplicateanalysisworkflow(portal):
    wf_id = "bika_duplicateanalysis_workflow"
    logger.info("Getting candidates for role mappings: {} ...".format(wf_id))
    workflow = get_workflow_by_id(portal, wf_id)

    candidates = list()
    if TransitionVerify not in workflow.states.to_be_verified.permissions:
        candidates.append(
            (wf_id,
             dict(portal_type="DuplicateAnalysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Duplicate Analysis Workflow: unasssigned
    if "unassigned" in workflow.states:
        candidates.append(
            (wf_id,
             dict(portal_type="DuplicateAnalysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Analysis workflow: "Modify portal content" for "assigned"
    if "Modify portal content" not in workflow.states.assigned.permissions:
        candidates.append(
            (wf_id,
             dict(portal_type="DuplicateAnalysis",
                  review_state=["assigned"]),
             CATALOG_ANALYSIS_LISTING))

    # Duplicate Analysis workflow: multi-verify transition
    if "multi_verify" not in workflow.transitions:
        candidates.append(
            (wf_id,
             dict(portal_type="DuplicateAnalysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))
    return candidates


def get_rm_candidates_for_analysisworkfklow(portal):
    wf_id = "bika_analysis_workflow"
    logger.info("Getting candidates for role mappings: {} ...".format(wf_id))
    workflow = get_workflow_by_id(portal, wf_id)

    candidates = list()
    if TransitionVerify not in workflow.states.to_be_verified.permissions:
        candidates.append(
            (wf_id,
             dict(portal_type="Analysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Analysis workflow: multi-verify transition
    if "multi_verify" not in workflow.transitions:
        candidates.append(
            (wf_id,
             dict(portal_type="Analysis",
                  review_state=["to_be_verified", "sample_received"]),
             CATALOG_ANALYSIS_LISTING))

    # Analysis workflow: "Modify portal content" for "unassigned"
    if "unassigned" in workflow.states:
        if "Modify portal content" not in workflow.states.unassigned.permissions:
            candidates.append(
                (wf_id,
                 dict(portal_type="Analysis",
                      review_state=["unassigned"]),
                 CATALOG_ANALYSIS_LISTING))

    # Analysis workflow: "Modify portal content" for "assigned"
    if "assigned" in workflow.states:
        if "Modify portal content" not in workflow.states.assigned.permissions:
            candidates.append(
                (wf_id,
                 dict(portal_type="Analysis",
                      review_state=["assigned"]),
                 CATALOG_ANALYSIS_LISTING))

    # Added new state "registered" in analysis_workflow. Also, new field
    # permissions in analysis_workflow, duplicate_workflow and reference_wf
    # Note this also affects ReferenceAnalysis and DuplicateAnalysis
    if "initialize" not in workflow.transitions:
        candidates.append(
            (wf_id,
             dict(not_review_state=["published"]),
             CATALOG_ANALYSIS_LISTING)
        )

    # Just in case (some buddies use 'retract' in 'verified' state)
    candidates.append(
        (wf_id,
         dict(portal_type="Analysis",
              review_state=["verified"]),
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
    query = dict(portal_type=["Analysis", "DuplicateAnalysis"],
                 review_state=affected_rs)
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        # Set state
        analysis = api.get_object(brain)
        target_state = "registered"
        if analysis.getWorksheet():
            target_state = "assigned"
        elif IDuplicateAnalysis.providedBy(analysis):
            logger.error("Duplicate analysis {} without worksheet!".
                         format(api.get_id(analysis)))
            continue
        else:
            request = analysis.getRequest()
            if request.getDateReceived():
                target_state = "unassigned"

        if num % 100 == 0:
            logger.info("Restoring state to '{}': {}/{}"
                        .format(target_state, num, total))

        changeWorkflowState(analysis, wf_id, target_state)

        # Update role mappings
        workflow.updateRoleMappingsFor(analysis)

        # Reindex
        analysis.reindexObject()


def remove_attachment_due_from_analysis_workflow(portal):
    logger.info("Removing attachment_due state from analysis workflow ...")
    wf_id = "bika_analysis_workflow"
    affected_rs = ["attachment_due"]
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    query = dict(review_state=affected_rs)
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        analysis = api.get_object(brain)
        target_state = "unassigned"
        if analysis.getWorksheet():
            target_state = "assigned"
        elif IRequestAnalysis.providedBy(analysis):
            if not IDuplicateAnalysis.providedBy(analysis):
                request = analysis.getRequest()
                if not request.getDateReceived():
                    target_state = "registered"

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


def rollback_to_receive_inconsistent_ars(portal):
    logger.info("Rolling back inconsistent Analysis Requests ...")
    review_states = ["to_be_verified"]
    query = dict(portal_type="AnalysisRequest", review_state=review_states)
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        request = api.get_object(brain)
        if not isTransitionAllowed(request, "rollback_to_receive"):
            total -= 1
            continue

        if num % 100 == 0:
            logger.info("Rolling back inconsistent AR '{}': {}/{}"
                        .format(request.getId(), num, total))

        do_action_for(request, "rollback_to_receive")


def rollback_to_open_inconsistent_ars(portal):
    logger.info("Rolling back inconsistent Worksheets ...")
    review_states = ["to_be_verified"]
    query = dict(portal_type="Worksheet", review_state=review_states)
    brains = api.search(query, CATALOG_WORKSHEET_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        ws = api.get_object(brain)
        if not isTransitionAllowed(ws, "rollback_to_open"):
            total -= 1
            continue

        if num % 100 == 0:
            logger.info("Rolling back inconsistent Worksheet '{}': {}/{}"
                        .format(ws.getId(), num, total))

        do_action_for(ws, "rollback_to_open")


def update_role_mappings(portal, queries):
    logger.info("Updating role mappings ...")
    processed = dict()
    for rm_query in queries:
        wf_tool = api.get_tool("portal_workflow")
        wf_id = rm_query[0]
        workflow = wf_tool.getWorkflowById(wf_id)

        query = rm_query[1].copy()
        exclude_states = []
        if 'not_review_state' in query:
            exclude_states = query.get('not_review_state', [])
            del query['not_review_state']

        brains = api.search(query, rm_query[2])
        total = len(brains)
        for num, brain in enumerate(brains):
            if num % 100 == 0:
                logger.info("Updating role mappings '{0}': {1}/{2}"
                            .format(wf_id, num, total))
            if api.get_uid(brain) in processed.get(wf_id, []):
                # Already processed, skip
                continue

            if api.get_workflow_status_of(brain) in exclude_states:
                # We explicitely want to exclude objs in these states
                continue

            workflow.updateRoleMappingsFor(api.get_object(brain))
            if wf_id not in processed:
                processed[wf_id] = []
            processed[wf_id].append(api.get_uid(brain))


def add_worksheet_indexes(portal):
    """Add indexes for better worksheet handling
    """
    logger.info("Adding worksheet indexes")

    add_index(portal, catalog_id="bika_analysis_catalog",
              index_name="getCategoryTitle",
              index_attribute="getCategoryTitle",
              index_metatype="FieldIndex")


def remove_bika_listing_resources(portal):
    """Remove all bika_listing resources
    """
    logger.info("Removing bika_listing resouces")

    REMOVE_JS = [
        "++resource++bika.lims.js/bika.lims.bikalisting.js",
        "++resource++bika.lims.js/bika.lims.bikalistingfilterbar.js",
    ]

    REMOVE_CSS = [
        "bika_listing.css",
    ]

    for js in REMOVE_JS:
        logger.info("********** Unregistering JS %s" % js)
        portal.portal_javascripts.unregisterResource(js)

    for css in REMOVE_CSS:
        logger.info("********** Unregistering CSS %s" % css)
        portal.portal_css.unregisterResource(css)


def hide_samples(portal):
    """Removes samples views from everywhere, related indexes, etc.
    """
    logger.info("Removing Samples from navbar ...")
    if "samples" in portal:
        portal.manage_delObjects(["samples"])

    def remove_samples_action(content_type):
        type_info = content_type.getTypeInfo()
        actions = map(lambda action: action.id, type_info._actions)
        for index, action in enumerate(actions, start=0):
            if action == 'samples':
                type_info.deleteActions([index])
                break

    def remove_actions_from_sample(sample):
        type_info = sample.getTypeInfo()
        idxs = [index for index, value in enumerate(type_info._actions)]
        type_info.deleteActions(idxs)

    logger.info("Removing Samples action view from inside Clients ...")
    for client in portal.clients.objectValues("Client"):
        remove_samples_action(client)

    logger.info("Removing Samples action view from inside Batches ...")
    for batch in portal.batches.objectValues("Batch"):
        remove_samples_action(batch)

    logger.info("Removing actions from inside Samples ...")
    for sample in api.search(dict(portal_type="Sample"), "bika_catalog"):
        remove_actions_from_sample(api.get_object(sample))
    commit_transaction(portal)


def fix_ar_analyses_inconsistencies(portal):
    """Fixes inconsistencies between analyses and the ARs they belong to when
    the AR is in a "cancelled", "invalidated" or "rejected state
    """
    def fix_analyses(request, status):
        wf_id = "bika_analysis_workflow"
        workflow = api.get_tool("portal_workflow").getWorkflowById(wf_id)
        review_states = ['assigned', 'unassigned', 'to_be_verified']
        query = dict(portal_type="Analysis",
                     getRequestUID=api.get_uid(request),
                     review_state=review_states)
        for brain in api.search(query, CATALOG_ANALYSIS_LISTING):
            analysis = api.get_object(brain)
            # If the analysis is assigned to a worksheet, unassign first
            ws = analysis.getWorksheet()
            if ws:
                remove_analysis_from_worksheet(analysis)
                reindex_request(analysis)

            # Force the new state
            changeWorkflowState(analysis, wf_id, status)
            workflow.updateRoleMappingsFor(analysis)
            analysis.reindexObject(idxs=["review_state", "is_active"])

    def fix_ar_analyses(status, wf_state_id="review_state"):
        brains = api.search({wf_state_id: status},
                            CATALOG_ANALYSIS_REQUEST_LISTING)
        total = len(brains)
        for num, brain in enumerate(brains):
            if num % 100 == 0:
                logger.info("Fixing inconsistent analyses from {} ARs: {}/{}"
                            .format(status, num, total))
            fix_analyses(brain, status)

    logger.info("Fixing Analysis Request - Analyses inconsistencies ...")
    pool = ActionHandlerPool.get_instance()
    pool.queue_pool()
    fix_ar_analyses("cancelled")
    fix_ar_analyses("invalid")
    fix_ar_analyses("rejected")
    pool.resume()
    commit_transaction(portal)


def add_worksheet_progress_percentage(portal):
    """Adds getProgressPercentage metadata to worksheets catalog
    """
    add_metadata(portal, CATALOG_WORKSHEET_LISTING, "getProgressPercentage")
    logger.info("Reindexing Worksheets ...")
    query = dict(portal_type="Worksheet")
    brains = api.search(query, CATALOG_WORKSHEET_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Reindexing open Worksheets: {}/{}"
                        .format(num, total))
        worksheet = api.get_object(brain)
        worksheet.reindexObject()


def remove_get_department_uids(portal):
    """Removes getDepartmentUIDs indexes and metadata
    """
    logger.info("Removing filtering by department ...")
    del_index(portal, "bika_catalog", "getDepartmentUIDs")
    del_index(portal, "bika_setup_catalog", "getDepartmentUID")
    del_index(portal, CATALOG_ANALYSIS_REQUEST_LISTING, "getDepartmentUIDs")
    del_index(portal, CATALOG_WORKSHEET_LISTING, "getDepartmentUIDs")
    del_index(portal, CATALOG_ANALYSIS_LISTING, "getDepartmentUID")

    del_metadata(portal, CATALOG_ANALYSIS_REQUEST_LISTING, "getDepartmentUIDs")
    del_metadata(portal, CATALOG_WORKSHEET_LISTING, "getDepartmentUIDs")
    del_metadata(portal, CATALOG_ANALYSIS_LISTING, "getDepartmentUID")


def decouple_analysis_requests_from_cancellation_workflow(portal):
    logger.info("Decoupling Analysis Requests from cancellation_workflow ...")
    wf_id = "bika_ar_workflow"
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    query = dict(portal_type="AnalysisRequest", cancellation_state="cancelled")
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if brain.review_state == "cancelled":
            continue
        if num % 100 == 0:
            logger.info("Resolving state to 'cancelled': {}/{}"
                        .format(num, total))
        # Set state
        analysis_request = api.get_object(brain)
        if api.get_workflow_status_of(analysis_request) == "cancelled":
            # The state of the analysis request is fine, only reindex
            analysis_request.reindexObject(idxs=["is_active", "review_state"])
            continue

        changeWorkflowState(analysis_request, wf_id, "cancelled")
        # Update role mappings
        workflow.updateRoleMappingsFor(analysis_request)
        # Reindex
        analysis_request.reindexObject(idxs=["is_active", "review_state"])


def decouple_analysisrequests_from_sample(portal):
    logger.info("Removing sample workflow ...")
    del_index(portal, "bika_catalog", "getSampleID")
    del_index(portal, "bika_catalog", "getSampleUID")
    del_index(portal, "bika_catalog", "getDisposalDate")
    del_index(portal, "bika_catalog", "getBatchUIDs")
    del_index(portal, CATALOG_ANALYSIS_LISTING, "getSamplePartitionUID")
    del_index(portal, CATALOG_ANALYSIS_LISTING, "getSampleUID")
    del_index(portal, CATALOG_ANALYSIS_LISTING, "getSampleConditionUID")
    del_index(portal, CATALOG_ANALYSIS_REQUEST_LISTING, "getSampleID")
    del_index(portal, CATALOG_ANALYSIS_REQUEST_LISTING, "getSampleUID")
    del_metadata(portal, "bika_catalog", "getSampleID")
    del_metadata(portal, "bika_catalog", "getBatchUIDs")
    del_metadata(portal, CATALOG_ANALYSIS_LISTING, "getExpiryDate")
    del_metadata(portal, CATALOG_ANALYSIS_LISTING, "getSamplePartitionID")
    del_metadata(portal, CATALOG_ANALYSIS_REQUEST_LISTING, "getSampleID")
    del_metadata(portal, CATALOG_ANALYSIS_REQUEST_LISTING, "getSampleUID")
    del_metadata(portal, CATALOG_ANALYSIS_REQUEST_LISTING, "getSampleURL")


def fix_analysisrequests_in_sampled_status(portal):
    logger.info("Resolving status 'sample' from Analysis Requests ...")
    wf_id = "bika_ar_workflow"
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    query = dict(portal_type="AnalysisRequest", review_state="sampled")
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Resolving state to 'sample_due': {}/{}"
                        .format(num, total))
        analysis_request = api.get_object(brain)
        changeWorkflowState(analysis_request, wf_id, "sample_due")
        workflow.updateRoleMappingsFor(analysis_request)
        analysis_request.reindexObject(idxs=["review_state"])


def port_analysis_request_proxy_fields(portal):
    logger.info("Purging Analysis Request Proxy Fields ...")

    def set_value(analysis_request, field_name, field_value):
        ar_field = analysis_request.Schema()[field_name]
        if ar_field.type == 'uidreference':
            if api.is_object(field_value):
                field_value = api.get_uid(field_value)
            elif not api.is_uid(field_value):
                return
        ar_field.set(analysis_request, field_value)

    def unlink_proxy_fields(sample_brain, analysis_request=None):
        processed_fields = []
        sample_obj = api.get_object(sample_brain)
        if not analysis_request:
            for ar in sample_obj.getAnalysisRequests():
                processed_fields.extend(unlink_proxy_fields(sample_brain, ar))
                ar.reindexObject()
            return list(set(processed_fields))

        for field_id in PROXY_FIELDS_TO_PURGE:
            field_value = None
            try:
                field = sample_obj.Schema().getField(field_id)
                field_value = field.get(sample_obj)
            except AttributeError:
                logger.warn("Field {} not found for {}"
                            .format(field_id, sample_obj.getId()))
            if not field_value:
                continue
            set_value(analysis_request, field_id, field_value)
            processed_fields.append(field_id)
        sample_obj.setMigrated(True)
        sample_obj.reindexObject(idxs="isValid")
        return processed_fields

    start = time.time()

    # We will use this index to keep track of the Samples that have been
    # processed already. This index will be added later for Reference Samples,
    # so is not an index only for this migration stuff, but we add the index
    # here so the samples processed are labeled as soon as possible
    add_index(portal, catalog_id="bika_catalog",
              index_name="isValid",
              index_attribute="isValid",
              index_metatype="BooleanIndex")

    query = dict(portal_type="Sample", isValid=False)
    brains = api.search(query, "bika_catalog")
    total = len(brains)
    need_commit = False
    for num, brain in enumerate(brains):
        need_commit = True
        if num % 10 == 0:
            logger.info("Purging Analysis Requests' ProxyField: {}/{}"
                        .format(num, total))
        processed_fields = unlink_proxy_fields(brain)
        if num > 0 and num % 1000 == 0:
            # This a very RAM consuming thing, so better to keep doing
            # transaction commits every now and then
            commit_transaction(portal)
            need_commit = False

    if need_commit:
        commit_transaction(portal)
    end = time.time()
    logger.info("Purging Analysis Request Proxy Fields took {:.2f}s"
                .format(end - start))

def commit_transaction(portal):
    start = time.time()
    logger.info("Commit transaction ...")
    transaction.commit()
    end = time.time()
    logger.info("Commit transaction ... Took {:.2f}s [DONE]"
                .format(end - start))


def change_analysis_requests_id_formatting(portal, p_type="AnalysisRequest"):
    """Applies the system's Sample ID Formatting to Analysis Request
    """
    ar_id_format = dict(
        form='{sampleType}-{seq:04d}',
        portal_type='AnalysisRequest',
        prefix='analysisrequest',
        sequence_type='generated',
        counter_type='',
        split_length=1)

    bs = portal.bika_setup
    id_formatting = bs.getIDFormatting()
    ar_format = filter(lambda id: id["portal_type"] == p_type, id_formatting)
    if p_type=="AnalysisRequest":
        logger.info("Set ID Format for Analysis Request portal_type ...")
        if not ar_format or "sample" in ar_format[0]["form"]:
            # Copy the ID formatting set for Sample
            change_analysis_requests_id_formatting(portal, p_type="Sample")
            return
        else:
            logger.info("ID Format for Analysis Request already set: {} [SKIP]"
                        .format(ar_format[0]["form"]))
            return
    else:
        ar_format = ar_format and ar_format[0].copy() or ar_id_format

    # Set the Analysis Request ID Format
    ar_id_format.update(ar_format)
    ar_id_format["portal_type"] ="AnalysisRequest"
    ar_id_format["prefix"] = "analysisrequest"
    set_id_format(portal, ar_id_format)

    # Find out the last ID for Sample and reseed AR to prevent ID already taken
    # errors on AR creation
    if p_type == "Sample":
        number_generator = getUtility(INumberGenerator)
        ar_keys = dict()
        ar_keys_prev = dict()
        for key, value in number_generator.storage.items():
            if "sample-" in key:
                ar_key = key.replace("sample-", "analysisrequest-")
                ar_keys[ar_key] = api.to_int(value, 0)
            elif "analysisrequest-" in key:
                ar_keys_prev[key] = api.to_int(value, 0)

        for key, value in ar_keys.items():
            if key in ar_keys_prev:
                # Maybe this upgrade step has already been run, so we don't
                # want the ar IDs to be reseeded again!
                if value <= ar_keys_prev[key]:
                    logger.info("ID for '{}' already seeded to '{}' [SKIP]"
                                .format(key, ar_keys_prev[key]))
                    continue
            logger.info("Seeding {} to {}".format(key, value))
            number_generator.set_number(key, value)


def set_id_format(portal, format):
    """Sets the id formatting in setup for the format provided
    """
    bs = portal.bika_setup
    if 'portal_type' not in format:
        return
    logger.info("Applying format {} for {}".format(format.get('form', ''),
                                                   format.get(
                                                       'portal_type')))
    portal_type = format['portal_type']
    ids = list()
    id_map = bs.getIDFormatting()
    for record in id_map:
        if record.get('portal_type', '') == portal_type:
            continue
        ids.append(record)
    ids.append(format)
    bs.setIDFormatting(ids)


def set_partitions_id_formatting(portal):
    """Sets the default id formatting for AR-like partitions
    """
    part_id_format = dict(
        form="{parent_ar_id}-P{partition_count:02d}",
        portal_type="AnalysisRequestPartition",
        prefix="analysisrequestretest",
        sequence_type="")
    set_id_format(portal, part_id_format)


def remove_stale_javascripts(portal):
    """Removes stale javascripts
    """
    logger.info("Removing stale javascripts ...")
    for js in JAVASCRIPTS_TO_REMOVE:
        logger.info("Unregistering JS %s" % js)
        portal.portal_javascripts.unregisterResource(js)


def remove_stale_indexes_from_bika_catalog(portal):
    """Removes stale indexes and metadata from bika_catalog. Most of these
    indexes and metadata were used for Samples, but they are no longer used.
    """
    logger.info("Removing stale indexes and metadata from bika_catalog ...")
    cat_id = "bika_catalog"
    indexes_to_remove = [
        "getAnalyst",
        "getAnalysts",
        "getAnalysisService",
        "getClientOrderNumber",
        "getClientReference",
        "getClientSampleID",
        "getContactTitle",
        "getDateDisposed",
        "getDateExpired",
        "getDateOpened",
        "getDatePublished",
        "getInvoiced",
        "getPreserver",
        "getSamplePointTitle",
        "getSamplePointUID",
        "getSampler",
        "getScheduledSamplingSampler",
        "getSamplingDate",
        "getWorksheetTemplateTitle",
        "BatchUID",
    ]
    metadata_to_remove = [
        "getAnalysts",
        "getClientOrderNumber",
        "getClientReference",
        "getClientSampleID",
        "getContactTitle",
        "getSamplePointTitle",
        "getAnalysisService",
        "getDatePublished",
    ]
    for index in indexes_to_remove:
        del_index(portal, cat_id, index)

    for metadata in metadata_to_remove:
        del_metadata(portal, cat_id, metadata)
    commit_transaction(portal)


def fix_worksheet_status_inconsistencies(portal):
    """Walks through open worksheets and transition them to 'verified' or
    'to_be_verified' if all their analyses are not in an open status
    """
    logger.info("Fixing worksheet inconsistencies ...")
    query = dict(portal_type="Worksheet",
                 review_state=["open", "to_be_verified"])
    brains = api.search(query, CATALOG_WORKSHEET_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        success = False
        if num % 100 == 0:
            logger.info("Fixing worksheet inconsistencies: {}/{}"
                        .format(num, total))
        # Note we don't check anything, WS guards for "submit" and "verify"
        # will take care of checking if the status of contained analyses allows
        # the transition.
        worksheet = api.get_object(brain)
        if api.get_workflow_status_of(worksheet) == "open":
            success, msg = do_action_for(worksheet, "submit")
        elif api.get_workflow_status_of(worksheet) == "to_be_verified":
            success, msg = do_action_for(worksheet, "verify")

        if success:
            logger.info("Worksheet {} transitioned to 'to_be_verified'"
                        .format(worksheet.getId()))
            success, msg = do_action_for(worksheet, "verify")
            if success:
                logger.info("Worksheet {} transitioned to 'verified'"
                            .format(worksheet.getId()))
    commit_transaction(portal)


def rename_analysis_requests_actions(portal):
    logger.info("Renaming 'Analysis Request' to 'Sample' ...")

    def rename_ar_action(content_type):
        if hasattr(content_type, "analysisrequests"):
            content_type.analysisrequests.setTitle("Samples")
            content_type.analysisrequests.reindexObject()
        if hasattr(content_type, "artemplates"):
            content_type.artemplates.setTitle("Sample Templates")
            content_type.artemplates.reindexObject()

    rename_ar_action(portal)
    for client in portal.clients.objectValues("Client"):
        rename_ar_action(client)

    for batch in portal.batches.objectValues("Batch"):
        rename_ar_action(batch)
    commit_transaction(portal)


def apply_analysis_request_partition_interface(portal):
    """Walks trhough all AR-like partitions registered in the system and
    applies the IAnalysisRequestPartition marker interface to them
    """
    logger.info("Applying 'IAnalysisRequestPartition' marker interface ...")
    query = dict(portal_type="AnalysisRequest", isRootAncestor=False)
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Applying 'IAnalysisRequestPartition' interface: {}/{}"
                        .format(num, total))
        ar = api.get_object(brain)
        if IAnalysisRequestPartition.providedBy(ar):
            continue
        if ar.getParentAnalysisRequest():
            alsoProvides(ar, IAnalysisRequestPartition)
    commit_transaction(portal)


def update_ar_listing_catalog(portal):
    """Add Indexes/Metadata to bika_catalog_analysisrequest_listing
    """
    cat_id = CATALOG_ANALYSIS_REQUEST_LISTING

    catalog = api.get_tool(cat_id)

    logger.info("Updating Indexes/Metadata of Catalog '{}'".format(cat_id))

    indexes_to_add = [
        # name, attribute, metatype
        ("getClientID", "getClientID", "FieldIndex"),
        ("is_active", "is_active", "BooleanIndex"),
    ]

    metadata_to_add = [
        "getClientID",
    ]

    for index in indexes_to_add:
        add_index(portal, cat_id, *index)

    for metadata in metadata_to_add:
        refresh = metadata not in catalog.schema()
        add_metadata(portal, cat_id, metadata, refresh_catalog=refresh)


def update_bika_catalog(portal):
    """Add Indexes/Metadata to bika_catalog
    """
    cat_id = "bika_catalog"

    catalog = api.get_tool(cat_id)

    logger.info("Updating Indexes/Metadata of Catalog '{}'".format(cat_id))

    indexes_to_add = [
        # name, attribute, metatype
        ("getClientID", "getClientID", "FieldIndex"),
        ("getClientBatchID", "getClientBatchID", "FieldIndex"),
        ("is_active", "is_active", "BooleanIndex"),
    ]

    metadata_to_add = [
        "getClientID",
        "getClientBatchID",
    ]

    for index in indexes_to_add:
        add_index(portal, cat_id, *index)

    for metadata in metadata_to_add:
        refresh = metadata not in catalog.schema()
        add_metadata(portal, cat_id, metadata, refresh_catalog=refresh)


def update_bika_analysis_catalog(portal):
    """Add Indexes/Metadata to bika_analysis_catalog
    """
    cat_id = "bika_analysis_catalog"

    catalog = api.get_tool(cat_id)

    logger.info("Updating Indexes/Metadata of Catalog '{}'".format(cat_id))

    indexes_to_add = [
        # name, attribute, metatype
        ("is_active", "is_active", "BooleanIndex"),
    ]

    metadata_to_add = [
    ]

    for index in indexes_to_add:
        add_index(portal, cat_id, *index)

    for metadata in metadata_to_add:
        refresh = metadata not in catalog.schema()
        add_metadata(portal, cat_id, metadata, refresh_catalog=refresh)


def update_bika_catalog_worksheet_listing(portal):
    """Add Indexes/Metadata to bika_analysis_catalog
    """
    cat_id = "bika_catalog_worksheet_listing"

    catalog = api.get_tool(cat_id)

    logger.info("Updating Indexes/Metadata of Catalog '{}'".format(cat_id))

    indexes_to_add = [
        # name, attribute, metatype
        ("is_active", "is_active", "BooleanIndex"),
    ]

    metadata_to_add = [
    ]

    for index in indexes_to_add:
        add_index(portal, cat_id, *index)

    for metadata in metadata_to_add:
        refresh = metadata not in catalog.schema()
        add_metadata(portal, cat_id, metadata, refresh_catalog=refresh)


def update_bika_setup_catalog(portal):
    """Add Indexes/Metadata to bika_setup_catalog
    """
    cat_id = "bika_setup_catalog"

    catalog = api.get_tool(cat_id)

    logger.info("Updating Indexes/Metadata of Catalog '{}'".format(cat_id))

    indexes_to_add = [
        # name, attribute, metatype
        ("is_active", "is_active", "BooleanIndex"),
    ]

    metadata_to_add = [
    ]

    for index in indexes_to_add:
        add_index(portal, cat_id, *index)

    for metadata in metadata_to_add:
        refresh = metadata not in catalog.schema()
        add_metadata(portal, cat_id, metadata, refresh_catalog=refresh)


def update_bika_catalog_report(portal):
    """Add Indexes/Metadata to bika_catalog_report
    """
    cat_id = "bika_catalog_report"

    catalog = api.get_tool(cat_id)

    logger.info("Updating Indexes/Metadata of Catalog '{}'".format(cat_id))

    indexes_to_add = [
        # name, attribute, metatype
        ("is_active", "is_active", "BooleanIndex"),
    ]

    metadata_to_add = [
    ]

    for index in indexes_to_add:
        add_index(portal, cat_id, *index)

    for metadata in metadata_to_add:
        refresh = metadata not in catalog.schema()
        add_metadata(portal, cat_id, metadata, refresh_catalog=refresh)


def update_portal_catalog(portal):
    """Add Indexes/Metadata to portal_catalog
    """
    cat_id = "portal_catalog"

    catalog = api.get_tool(cat_id)

    logger.info("Updating Indexes/Metadata of Catalog '{}'".format(cat_id))

    indexes_to_add = [
        # name, attribute, metatype
        ("is_active", "is_active", "BooleanIndex"),
    ]

    metadata_to_add = [
    ]

    for index in indexes_to_add:
        add_index(portal, cat_id, *index)

    for metadata in metadata_to_add:
        refresh = metadata not in catalog.schema()
        add_metadata(portal, cat_id, metadata, refresh_catalog=refresh)


def update_notify_on_sample_invalidation(portal):
    """The name of the Setup field was NotifyOnARRetract, so it was
    confusing. There was also two fields "NotifyOnRejection"
    """
    setup = api.get_setup()

    # NotifyOnARRetract --> NotifyOnSampleInvalidation
    old_value = setup.__dict__.get("NotifyOnARRetract", True)
    setup.setNotifyOnSampleInvalidation(old_value)

    # NotifyOnRejection --> NotifyOnSampleRejection
    old_value = setup.__dict__.get("NotifyOnRejection", False)
    setup.setNotifyOnSampleRejection(old_value)


def apply_analysis_request_retest_interface(portal):
    """Walks through all AR-like partitions registered in the system and
    applies the IAnalysisRequestRetest marker interface to them
    """
    logger.info("Applying 'IAnalysisRequestRetest' marker interface ...")
    query = dict(portal_type="AnalysisRequest")
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Applying 'IAnalysisRequestRetest' interface: {}/{}"
                        .format(num, total))
        ar = api.get_object(brain)
        if ar.getInvalidated():
            alsoProvides(ar, IAnalysisRequestRetest)
    commit_transaction(portal)


def set_retest_id_formatting(portal):
    """Sets the default id formatting for AR retests
    """
    part_id_format = dict(
        form="{parent_base_id}-{seq:02d}-R{seq:02d}",
        portal_type="AnalysisRequestRetest",
        prefix="analysisrequestretest",
        sequence_type="")
    set_id_format(portal, part_id_format)


def reindex_submitted_analyses(portal):
    """Reindex submitted analyses
    """
    logger.info("Reindex submitted analyses")
    brains = api.search({}, "bika_analysis_catalog")

    total = len(brains)
    logger.info("Processing {} analyses".format(total))

    for num, brain in enumerate(brains):
        # skip analyses which have an analyst
        if brain.getAnalyst:
            continue
        # reindex analyses which have no annalyst set, but a result
        if brain.getResult not in ["", None]:
            analysis = brain.getObject()
            analysis.reindexObject()
        if num > 0 and num % 5000 == 0:
            logger.info("Commiting reindexed analyses {}/{} ..."
                        .format(num, total))
            transaction.commit()


def fix_calculation_version_inconsistencies(portal):
    """Creates the first version of all Calculations that hasn't been yet edited
    See: https://github.com/senaite/senaite.core/pull/1260
    """
    logger.info("Fix Calculation version inconsistencies ...")
    brains = api.search({"portal_type": "Calculation"}, "bika_setup_catalog")
    total = len(brains)
    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Fix Calculation version inconsistencies: {}/{}"
                        .format(num, total))
        calc = api.get_object(brain)
        version = getattr(calc, "version_id", None)
        if version is None:
            pr = api.get_tool("portal_repository")
            pr.save(obj=calc, comment="First version")
            logger.info("First version created for {}".format(calc.Title()))
    logger.info("Fix Calculation version inconsistencies [DONE]")

