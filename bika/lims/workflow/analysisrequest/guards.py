# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName

from bika.lims import api
from bika.lims import logger
from bika.lims.workflow import doActionFor
from bika.lims.workflow import getCurrentState
from bika.lims.workflow import isActive
from bika.lims.workflow import isBasicTransitionAllowed
from bika.lims.workflow import isTransitionAllowed
from bika.lims.workflow import wasTransitionPerformed
from bika.lims.workflow.analysis import guards as analysis_guards


def are_analyses_valid(analysis_request, target_states, skip_states=None):
    """Returns true if the analysis request does not contain any analysis in a
    non-permitted state and it has at least one analysis in the target_state.
    """
    if not skip_states:
        _skip_states = ['cancelled', 'rejected', 'retracted']
        return are_analyses_valid(analysis_request, target_states, _skip_states)

    if isinstance(target_states, basestring):
        _target_states = [target_states]
        return are_analyses_valid(analysis_request, _target_states, skip_states)

    valid_analyses = False
    allowed_states = list(set(skip_states + target_states))
    for an in analysis_request.getAnalyses(full_objects=True):
        an_state = api.get_workflow_status_of(an)
        if an_state not in allowed_states:
            return False
        valid_analyses = valid_analyses or an_state in target_states
    return valid_analyses


def to_be_preserved(obj):
    """ Returns True if the Sample from this AR needs to be preserved
    Returns false if the Analysis Request has no Sample assigned yet or
    does not need to be preserved
    Delegates to Sample's guard_to_be_preserved
    """
    sample = obj.getSample()
    return sample and sample.guard_to_be_preserved()


def schedule_sampling(obj):
    """
    Prevent the transition if:
    - if the user isn't part of the sampling coordinators group
      and "sampling schedule" checkbox is set in bika_setup
    - if no date and samples have been defined
      and "sampling schedule" checkbox is set in bika_setup
    """
    if obj.bika_setup.getScheduleSamplingEnabled() and \
            isBasicTransitionAllowed(obj):
        return True
    return False


def receive(obj):
    return isBasicTransitionAllowed(obj)


def guard_create_partitions(analysis_request):
    """Returns true if partitions can be created using the analysis request
    passed in as the source.
    """
    if not analysis_request.bika_setup.getShowPartitions():
        # If partitions are disabled in Setup, return False
        return False

    if not isBasicTransitionAllowed(analysis_request):
        return False

    if analysis_request.isPartition():
        # Do not allow the creation of partitions from partitions
        return False

    return True


def guard_submit(analysis_request):
    """Return whether the transition "submit" can be performed or not.
    An Analysis Request can only be submitted if all (active) analyses it
    contains have been submitted.
    """
    return are_analyses_valid(analysis_request, ["to_be_verified"])


def guard_verify(analysis_request):
    """Returns True if 'verify' transition can be applied to the Analysis
    Request passed in. This is, returns true if all the analyses that contains
    have already been verified. Those analyses that are in an inactive state
    (cancelled, inactive) are dismissed, but at least one analysis must be in
    an active state (and verified), otherwise always return False. If the
    Analysis Request is in inactive state (cancelled/inactive), returns False
    Note this guard depends entirely on the current status of the children
    :returns: true or false
    """
    return are_analyses_valid(analysis_request, ["verified"])


def prepublish(obj):
    """Returns True if 'prepublish' transition can be applied to the Analysis
    Request passed in.
    Returns true if the Analysis Request is active (not in a cancelled/inactive
    state), the 'publish' transition cannot be performed yet, and at least one
    of its analysis is under to_be_verified state or has been already verified.
    As per default DC workflow definition in bika_ar_workflow, note that
    prepublish does not transitions the Analysis Request to any other state
    different from the actual one, neither its children. This 'fake' transition
    is only used for the prepublish action to be displayed when the Analysis
    Request' status is other than verified, so the labman can generate a
    provisional report, also if results are not yet definitive.
    :returns: true or false
    """
    if not isBasicTransitionAllowed(obj):
        return False

    if isTransitionAllowed(obj, 'publish'):
        return False

    analyses = obj.getAnalyses(full_objects=True)
    for an in analyses:
        # If the analysis is not active, omit
        if not isActive(an):
            continue

        # Check if the current state is 'verified'
        status = getCurrentState(an)
        if status in ['verified', 'to_be_verified']:
            return True

    # This analysis request has no single result ready to be verified or
    # verified yet. In this situation, it doesn't make sense to publish a
    # provisional results reports without a single result to display
    return False


def publish(obj):
    """Returns True if 'publish' transition can be applied to the Analysis
    Request passed in. Returns true if the Analysis Request is active (not in
    a cancelled/inactive state). As long as 'publish' transition, in accordance
    with its DC workflow can only be performed if its previous state is
    verified or published, there is no need of additional validations.
    :returns: true or false
    """
    return isBasicTransitionAllowed(obj)


def guard_rollback_to_receive(analysis_request):
    """Return whether 'rollback_to_receive' transition can be performed or not
    """
    # Can rollback to receive if at least one analysis hasn't been submitted yet
    # or if all analyses have been rejected or retracted
    analyses = analysis_request.getAnalyses()
    skipped = 0
    for analysis in analyses:
        analysis_object = api.get_object(analysis)
        state = getCurrentState(analysis_object)
        if state in ["unassigned", "assigned"]:
            return True
        if state in ["retracted", "rejected"]:
            skipped += 1
    return len(analyses) == skipped


def guard_cancel(analysis_request):
    """Returns whether 'cancel' transition can be performed or not. Returns
    True only if all analyses are in "unassigned" status
    """
    # Ask to partitions
    for partition in analysis_request.getDescendants(all_descendants=False):
        if not isTransitionAllowed(partition, "cancel"):
            return False

    # Look through analyses
    for analysis in analysis_request.getAnalyses():
        analysis_object = api.get_object(analysis)
        if api.get_workflow_status_of(analysis_object) != "unassigned":
            return False

    return True


def guard_reinstate(analysis_request):
    """Returns whether 'reinstate" transition can be performed or not. Returns
    True only if this is not a partition or the parent analysis request can be
    reinstated
    """
    parent = analysis_request.getParentAnalysisRequest()
    return not parent or isTransitionAllowed(parent, "reinstate")
