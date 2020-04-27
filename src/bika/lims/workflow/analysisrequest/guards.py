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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.interfaces import IVerified, IInternalUse
from bika.lims.workflow import isTransitionAllowed

# States to be omitted in regular transitions
ANALYSIS_DETACHED_STATES = ['cancelled', 'rejected', 'retracted']


def guard_no_sampling_workflow(analysis_request):
    """Returns whether the transition "no_sampling_workflow" can be performed
    or not. Returns True when Sampling Workflow is not enabled in setup
    """
    return not analysis_request.getSamplingRequired()


def guard_to_be_sampled(analysis_request):
    """Returns whether the transition "to_be_sampled" can be performed or not.
    Returns True if Sampling Workflow is enabled for the analysis request
    """
    return analysis_request.getSamplingRequired()


def guard_schedule_sampling(analysis_request):
    """Return whether the transition "schedule_sampling" can be performed or not
    Returns True only when the schedule sampling workflow is enabled in setup.
    """
    return analysis_request.bika_setup.getScheduleSamplingEnabled()


def guard_create_partitions(analysis_request):
    """Returns true if partitions can be created using the analysis request
    passed in as the source.
    """
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
    Returns True if there is at least one analysis in a non-detached state and
    all analyses in a non-detached analyses have been submitted.
    """
    # Discard detached analyses
    analyses = analysis_request.getAnalyses(full_objects=True)
    analyses = filter(lambda an: api.get_workflow_status_of(an) not in
                                 ANALYSIS_DETACHED_STATES, analyses)

    # If not all analyses are for internal use, rely on "regular" analyses
    internals = map(IInternalUse.providedBy, analyses)
    omit_internals = not all(internals)

    analyses_ready = False
    for analysis in analyses:
        # Omit analyses for internal use
        if omit_internals and IInternalUse.providedBy(analysis):
            continue

        analysis_status = api.get_workflow_status_of(analysis)
        if analysis_status in ['assigned', 'unassigned', 'registered']:
            return False

        analyses_ready = True
    return analyses_ready


def guard_verify(analysis_request):
    """Returns whether the transition "verify" can be performed or not.
    Returns True if at there is at least one analysis in a non-dettached state
    and all analyses in a non-detached state are in "verified" state.
    """
    # Discard detached analyses
    analyses = analysis_request.getAnalyses(full_objects=True)
    analyses = filter(lambda an: api.get_workflow_status_of(an) not in
                                 ANALYSIS_DETACHED_STATES, analyses)

    # If not all analyses are for internal use, rely on "regular" analyses
    internals = map(IInternalUse.providedBy, analyses)
    omit_internals = not all(internals)

    analyses_ready = False
    for analysis in analyses:
        # Omit analyses for internal use
        if omit_internals and IInternalUse.providedBy(analysis):
            continue

        # All analyses must be in verified (or further) status
        if not IVerified.providedBy(analysis):
            return False

        analyses_ready = True
    return analyses_ready


def guard_prepublish(analysis_request):
    """Returns whether 'prepublish' transition can be perform or not. Returns
    True if the analysis request has at least one analysis in 'verified' or in
    'to_be_verified' status. Otherwise, return False
    """
    if IInternalUse.providedBy(analysis_request):
        return False

    valid_states = ['verified', 'to_be_verified']
    for analysis in analysis_request.getAnalyses():
        analysis = api.get_object(analysis)
        if api.get_workflow_status_of(analysis) in valid_states:
            return True
    return False


def guard_publish(analysis_request):
    """Returns whether the transition "publish" can be performed or not.
    Returns True if the analysis request is not labeled for internal use or if
    at least one of the contained analyses is not for internal use
    """
    if IInternalUse.providedBy(analysis_request):
        return False
    # Note we return True without checking anything else because this
    # transition is only available when sample is in verified status
    return True


def guard_rollback_to_receive(analysis_request):
    """Return whether 'rollback_to_receive' transition can be performed or not.
    Returns True if the analysis request has at least one analysis in 'assigned'
    or 'unassigned' status. Otherwise, returns False
    """
    skipped = 0
    valid_states = ['unassigned', 'assigned']
    skip_states = ['retracted', 'rejected']
    analyses = analysis_request.getAnalyses()
    for analysis in analyses:
        analysis = api.get_object(analysis)
        status = api.get_workflow_status_of(analysis)
        if status in valid_states:
            return True
        elif status in skip_states:
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
    cancellable_states = ["unassigned", "registered"]

    # also consider the detached states as cancellable
    cancellable_states += ANALYSIS_DETACHED_STATES

    for analysis in analysis_request.objectValues("Analysis"):
        if api.get_workflow_status_of(analysis) not in cancellable_states:
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


def guard_sample(analysis_request):
    """Returns whether 'sample' transition can be performed or not. Returns
    True only if the analysis request has the DateSampled and Sampler set or if
    the user belongs to the Samplers group
    """
    if analysis_request.getDateSampled() and analysis_request.getSampler():
        return True

    current_user = api.get_current_user()
    return "Sampler" in current_user.getRolesInContext(analysis_request)


def guard_reject(analysis_request):
    """Returns whether 'reject' transition can be performed or not. Returns
    True only if setup's isRejectionWorkflowEnabled is True
    """
    return analysis_request.bika_setup.isRejectionWorkflowEnabled()


def guard_detach(analysis_request):
    """Returns whether 'detach' transition can be performed or not. Returns True
    only if the sample passed in is a partition
    """
    # Detach transition can only be done to partitions
    return analysis_request.isPartition()
