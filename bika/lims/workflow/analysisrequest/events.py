# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.utils import changeWorkflowState
from bika.lims.utils.analysisrequest import create_retest
from bika.lims.workflow import doActionFor, getReviewHistoryActionsList, \
    get_prev_status_from_history
from bika.lims.workflow import getCurrentState
from bika.lims.workflow.analysisrequest import AR_WORKFLOW_ID


def _promote_transition(obj, transition_id):
    """Promotes the transition passed in to the object's parent
    :param obj: Analysis Request for which the transition has to be promoted
    :param transition_id: Unique id of the transition
    """
    sample = obj.getSample()
    if sample:
        doActionFor(sample, transition_id)


def after_no_sampling_workflow(obj):
    """Method triggered after a 'no_sampling_workflow' transition for the
    Analysis Request passed inis performed. Performs the same transition to the
    parent's Sample.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """

    # Do note that the 'no_sampling' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition neither the analyses nor partitions here
    _promote_transition(obj, 'no_sampling_workflow')


def after_sampling_workflow(obj):
    """Method triggered after a 'sampling_workflow' transition for the
    Analysis Request passed in is performed. Performs the same transition to
    the parent's Sample.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """

    # Do note that the 'sampling' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition neither the analyses nor partitions here
    _promote_transition(obj, 'sampling_workflow')


def after_preserve(obj):
    """Method triggered after a 'preserve' transition for the Analysis Request
    passed in is performed. Promotes the same transition to parent's Sample.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """

    # Do note that the 'preserve' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition neither the analyses nor partitions here
    _promote_transition(obj, 'preserve')


def after_schedule_sampling(obj):
    """Method triggered after a 'schedule_sampling' transition for the Analysis
    Request passed in is performed. Promotes the same transition to parent's
    Sample.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    _promote_transition(obj, 'schedule_sampling')


def after_sample(obj):
    """Method triggered after a 'sample' transition for the Analysis Request
    passed in is performed. Promotes sample transition to parent's sample
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    # Do note that the 'sample' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition neither the analyses nor partitions here
    _promote_transition(obj, 'sample')


def after_receive(obj):
    """Method triggered after a 'receive' transition for the Analysis Request
    passed in is performed. Responsible of triggering cascade actions such as
    transitioning the container (sample), as well as associated analyses.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    # Do note that the 'sample' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition neither the analyses nor partitions here
    _promote_transition(obj, 'receive')

    # Reindex the analyses this Analysis Request contains
    for analysis in obj.getAnalyses(full_objects=True):
        analysis.reindexObject()

def after_reject(obj):
    """Method triggered after a 'reject' transition for the Analysis Request
    passed in is performed. Transitions and sets the rejection reasons to the
    parent Sample. Also transitions the analyses assigned to the AR
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    sample = obj.getSample()
    if not sample:
        return

    if getCurrentState(sample) != 'rejected':
        doActionFor(sample, 'reject')
        reasons = obj.getRejectionReasons()
        sample.setRejectionReasons(reasons)

    # Deactivate all analyses from this Analysis Request
    ans = obj.getAnalyses(full_objects=True)
    for analysis in ans:
        doActionFor(analysis, 'reject')

    if obj.bika_setup.getNotifyOnRejection():
        # Import here to brake circular importing somewhere
        from bika.lims.utils.analysisrequest import notify_rejection
        # Notify the Client about the Rejection.
        notify_rejection(obj)


def after_retract(obj):
    """Method triggered after a 'retract' transition for the Analysis Request
    passed in is performed. Transitions and sets the analyses of the Analyses
    Request to retracted.
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    ans = obj.getAnalyses(full_objects=True)
    for analysis in ans:
        doActionFor(analysis, 'retract')


def after_invalidate(obj):
    """Function triggered after 'invalidate' transition for the Analysis
    Request passed in is performed. Creates a retest
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    create_retest(obj)


def after_attach(obj):
    """Method triggered after an 'attach' transition for the Analysis Request
    passed in is performed.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    # Don't cascade. Shouldn't be attaching ARs for now (if ever).
    pass


def after_submit(obj):
    """Function called after a 'submit' transition is triggered
    """
    # Promote to parent AR
    parent_ar = obj.getParentAnalysisRequest()
    if parent_ar:
        doActionFor(parent_ar, "submit")

    # Cascade to partitions
    parts = obj.getDescendants(all_descendants=False)
    for part in parts:
        doActionFor(part, "submit")


def after_verify(obj):
    """Method triggered after a 'verify' transition for the Analysis Request
    passed in is performed. Responsible of triggering cascade actions to
    associated analyses.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    # Promote to parent AR
    parent_ar = obj.getParentAnalysisRequest()
    if parent_ar:
        doActionFor(parent_ar, "verify")

    # Cascade to partitions
    parts = obj.getDescendants(all_descendants=False)
    for part in parts:
        doActionFor(part, "verify")


def after_publish(analysis_request):
    """Method triggered after an 'publish' transition for the Analysis Request
    passed in is performed. Performs the 'publish' transition to children.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    # Transition the children
    for analysis in analysis_request.getAnalyses(full_objects=True):
        doActionFor(analysis, 'publish')

    # Cascade to partitions
    parts = analysis_request.getDescendants(all_descendants=False)
    for part in parts:
        doActionFor(part, "publish")


def after_reinstate(analysis_request):
    """Method triggered after a 'reinstate' transition for the Analysis Request
    passed in is performed. Reinstates all parent analysis requests, as well as
    the contained analyses
    """
    # Cascade to partitions
    for part in analysis_request.getDescendants(all_descendants=False):
        doActionFor(part, "reinstate")

    # Cascade to analyses
    for analysis in analysis_request.objectValues("Analysis"):
        doActionFor(analysis, 'reinstate')

    # Force the transition to previous state before the request was cancelled
    prev_status = get_prev_status_from_history(analysis_request, "cancelled")
    changeWorkflowState(analysis_request, AR_WORKFLOW_ID, prev_status,
                        action="reinstate",
                        actor=api.get_current_user().getId())
    analysis_request.reindexObject()


def after_cancel(analysis_request):
    """Method triggered after a 'cancel' transition for the Analysis Request
    passed in is performed. Cascades this transition to its analyses and
    partitions.
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    # Cascade to partitions
    for part in analysis_request.getDescendants(all_descendants=False):
        doActionFor(part, "cancel")

    # Cascade to analyses. We've cascaded to partitions already, so there is
    # no need to cascade to analyses from partitions again, but through the
    # analyses directly bound to the current Analysis Request.
    for analysis in analysis_request.objectValues("Analysis"):
        doActionFor(analysis, "cancel")


def after_rollback_to_receive(analysis_request):
    """Function triggered after rollback_to_receive transition finishes
    """
    pass
