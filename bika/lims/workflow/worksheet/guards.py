# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.workflow import isBasicTransitionAllowed
from bika.lims.workflow import wasTransitionPerformed


def _children_are_ready(obj, transition_id, dettached_states=None):
    """Returns true if the children of the object passed in (worksheet) have
    been all transitioned in accordance with the 'transition_id' passed in. If
    detached_states is provided, children with those states are dismissed, so
    they will not be taken into account in the evaluation. Nevertheless, at
    least one child with for which the transition_id performed is required for
    this function to return true (if all children are in detached states, it
    always return False).
    """
    query = dict(getWorksheetUID=api.get_uid(obj))
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    if not brains:
        return False
    detached_count = 0

    for brain in brains:
        if dettached_states and brain.review_state in dettached_states:
            detached_count += 1
            # dismiss the brain and skip the rest of the checks
            continue
        if not api.is_active(brain):
            return False
        analysis = api.get_object(brain)
        if not wasTransitionPerformed(analysis, transition_id):
            return False

    if detached_count == len(brains):
        # If all brains are in a detached state, it means that the
        # condition of at least having one child for which the
        # transition is performed is not satisfied so return False
        return False
    return True


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
