# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from bika.lims.workflow import doActionFor
from bika.lims.workflow import getCurrentState
from bika.lims.workflow import isActive
from bika.lims.workflow import isBasicTransitionAllowed
from bika.lims.workflow import isTransitionAllowed
from bika.lims.workflow import wasTransitionPerformed
from bika.lims.workflow.analysis import guards as analysis_guards


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


def sample_prep(obj):
    sample = obj.getSample()
    return sample.guard_sample_prep_transition()


def sample_prep_complete(obj):
    sample = obj.getSample()
    return sample.guard_sample_prep_complete_transition()


def assign(obj):
    """Allow or disallow transition depending on our children's states
    """
    # TODO Workflow Assign AR - To revisit. Is there any reason why we want an
    # AR to be in an 'assigned' state?. If no, remove the transition from the
    # workflow definition, as well as from here and from content.analysisrequest
    return False

    if not isBasicTransitionAllowed(obj):
        return False
    return True


def unassign(obj):
    """Allow or disallow transition depending on our children's states
    """
    # TODO Workflow UnAssign AR - To revisit. Is there any reason why we want an
    # AR to be in an 'assigned' state?. If no, remove the transition from the
    # workflow definition, as well as from here and from content.analysisrequest
    return False

    if not isBasicTransitionAllowed(obj):
        return False
    return True


def verify(obj):
    """Returns True if 'verify' transition can be applied to the Analysis
    Request passed in. This is, returns true if all the analyses that contains
    have already been verified. Those analyses that are in an inactive state
    (cancelled, inactive) are dismissed, but at least one analysis must be in
    an active state (and verified), otherwise always return False. If the
    Analysis Request is in inactive state (cancelled/inactive), returns False
    Note this guard depends entirely on the current status of the children
    :returns: true or false
    """
    if not isBasicTransitionAllowed(obj):
        return False

    analyses = obj.getAnalyses(full_objects=True)
    invalid = 0
    for an in analyses:
        # The analysis has already been verified?
        if wasTransitionPerformed(an, 'verify'):
            continue

        # Maybe the analysis is in an 'inactive' state?
        if not isActive(an):
            invalid += 1
            continue

        # Maybe the analysis has been rejected or retracted?
        dettached = ['rejected', 'retracted', 'attachments_due']
        status = getCurrentState(an)
        if status in dettached:
            invalid += 1
            continue

        # At this point we can assume this analysis is an a valid state and
        # could potentially be verified, but the Analysis Request can only be
        # verified if all the analyses have been transitioned to verified
        return False

    # Be sure that at least there is one analysis in an active state, it
    # doesn't make sense to verify an Analysis Request if all the analyses that
    # contains are rejected or cancelled!
    return len(analyses) - invalid > 0


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
