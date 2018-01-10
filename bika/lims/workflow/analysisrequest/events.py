# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from DateTime import DateTime

from bika.lims.workflow import doActionFor
from bika.lims.workflow import getCurrentState


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
    obj.setDateReceived(DateTime())
    obj.reindexObject(idxs=["getDateReceived", ])

    # Do note that the 'sample' transition for Sample already transitions
    # all the analyses associated to all the sample partitions, so there
    # is no need to transition neither the analyses nor partitions here
    _promote_transition(obj, 'receive')


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


def after_verify(obj):
    """Method triggered after a 'verify' transition for the Analysis Request
    passed in is performed. Responsible of triggering cascade actions to
    associated analyses.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    pass


def after_publish(obj):
    """Method triggered after an 'publish' transition for the Analysis Request
    passed in is performed. Performs the 'publish' transition to children.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    # Transition the children
    ans = obj.getAnalyses(full_objects=True)
    for analysis in ans:
        doActionFor(analysis, 'publish')


def after_reinstate(obj):
    """Method triggered after a 'reinstate' transition for the Analysis Request
    passed in is performed. Activates all analyses contained in the object.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    ans = obj.getAnalyses(full_objects=True, cancellation_state='cancelled')
    for analysis in ans:
        doActionFor(analysis, 'reinstate')


def after_cancel(obj):
    """Method triggered after a 'cancel' transition for the Analysis Request
    passed in is performed. Deactivates all analyses contained in the object.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Analysis Request affected by the transition
    :type obj: AnalysisRequest
    """
    ans = obj.getAnalyses(full_objects=True, cancellation_state='active')
    for analysis in ans:
        doActionFor(analysis, 'cancel')
