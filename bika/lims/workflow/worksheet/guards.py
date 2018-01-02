# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.workflow import getCurrentState
from bika.lims.workflow import isActive
from bika.lims.workflow import isBasicTransitionAllowed
from bika.lims.workflow import wasTransitionPerformed


def _children_are_ready(obj, transition_id, dettached_states=None):
    """Returns true if the children of the object passed in (worksheet) have
    been all transitioned in accordance with the 'transition_id' passed in. If
    dettached_states is provided, children with those states are dismissed, so
    they will not be taken into account in the evaluation. Nevertheless, at
    least one child with for which the transition_id performed is required for
    this function to return true (if all children are in dettached states, it
    always return False).
    """
    analyses = obj.getAnalyses()
    invalid = 0
    for an in analyses:
        # The analysis has already been transitioned?
        if wasTransitionPerformed(an, transition_id):
            continue

        # Maybe the analysis is in an 'inactive' state?
        if not isActive(an):
            invalid += 1
            continue

        # Maybe the analysis is in a dettached state?
        if dettached_states:
            status = getCurrentState(an)
            if status in dettached_states:
                invalid += 1
                continue

        # At this point we can assume this analysis is an a valid state and
        # could potentially be transitioned, but the Worksheet can only be
        # transitioned if all the analyses have been transitioned previously
        return False

    # Be sure that at least there is one analysis in an active state, it
    # doesn't make sense to transition a Worksheet if all the analyses that
    # contains are not valid
    return len(analyses) - invalid > 0


def submit(obj):
    """Returns if 'submit' transition can be applied to the worksheet passed in.
    By default, the target state for the 'submit' transition for a worksheet is
    'to_be_verified', so this guard returns true if all the analyses assigned
    to the worksheet have already been submitted. Those analyses that are in a
    non-valid state (cancelled, inactive) are dismissed in the evaluation, but
    at least one analysis must be in an active state (and submitted) for this
    guard to return True. Otherwise, always returns False.
    Note this guard depends entirely on the current status of the children.
    """
    if not isBasicTransitionAllowed(obj):
        return False

    dettached = ['rejected', 'retracted', 'attachment_due']
    return _children_are_ready(obj, 'submit', dettached)


def verify(obj):
    """Returns True if 'verify' transition can be applied to the Worksheet
    passed in. This is, returns true if all the analyses assigned
    have already been verified. Those analyses that are in an inactive state
    (cancelled, inactive) are dismissed, but at least one analysis must be in
    an active state (and verified), otherwise always return False.
    Note this guard depends entirely on the current status of the children
    :returns: true or false
    """
    if not isBasicTransitionAllowed(obj):
        return False

    dettached = ['rejected', 'retracted', 'attachment_due']
    return _children_are_ready(obj, 'verify', dettached)
