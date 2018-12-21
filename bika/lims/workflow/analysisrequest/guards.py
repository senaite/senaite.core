# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.workflow import getCurrentState
from bika.lims.workflow import isActive
from bika.lims.workflow import isTransitionAllowed

# States to be omitted in regular transitions
ANALYSIS_DETTACHED_STATES = ['cancelled', 'rejected', 'retracted']

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
    return obj.bika_setup.getScheduleSamplingEnabled()


def guard_create_partitions(analysis_request):
    """Returns true if partitions can be created using the analysis request
    passed in as the source.
    """
    if not analysis_request.bika_setup.getShowPartitions():
        # If partitions are disabled in Setup, return False
        return False

    if analysis_request.isPartition():
        # Do not allow the creation of partitions from partitions
        return False

    # Allow only the creation of partitions if all analyses from the Analysis
    # Request are in unassigned state. Otherwise, we could end up with
    # inconsistencies, because original analyses are deleted when the partition
    # is created. Note here we exclude analyses from children (partitions).
    analyses = analysis_request.objectValues("Analysis")
    for analysis in analyses:
        if api.get_workflow_status_of(analysis) != "unassigned":
            return False
    return analyses and True or False


def guard_submit(analysis_request):
    """Return whether the transition "submit" can be performed or not.
    Returns True if there is at least one analysis in a non-dettached state and
    all analyses in a non-dettached analyses have been submitted.
    """
    analyses_ready = False
    for analysis in analysis_request.getAnalyses():
        analysis_status = api.get_workflow_status_of(api.get_object(analysis))
        if analysis_status in ANALYSIS_DETTACHED_STATES:
            continue
        if analysis_status in ['assigned', 'unassigned']:
            return False
        analyses_ready = True
    return analyses_ready


def guard_verify(analysis_request):
    """Returns whether the transition "verify" can be performed or not.
    Returns True if at there is at least one analysis in a non-dettached state
    and all analyses in a non-dettached state are in "verified" state.
    """
    analyses_ready = False
    for analysis in analysis_request.getAnalyses():
        analysis_status = api.get_workflow_status_of(api.get_object(analysis))
        if analysis_status in ANALYSIS_DETTACHED_STATES:
            continue
        if analysis_status != 'verified':
            return False
        analyses_ready = True
    return analyses_ready


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

    # Look through analyses. We've checked the partitions already, so there is
    # no need to look through analyses from partitions again, but through the
    # analyses directly bound to the current Analysis Request.
    for analysis in analysis_request.objectValues("Analysis"):
        if api.get_workflow_status_of(analysis) != "unassigned":
            return False

    return True


def guard_reinstate(analysis_request):
    """Returns whether 'reinstate" transition can be performed or not. Returns
    True only if this is not a partition or the parent analysis request can be
    reinstated or is not in a cancelled state
    """
    parent = analysis_request.getParentAnalysisRequest()
    if not parent:
        return True
    if api.get_workflow_status_of(parent) != "cancelled":
        return True
    return isTransitionAllowed(parent, "reinstate")
