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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.workflow import isTransitionAllowed
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
    detached_count = 0
    analyses = obj.getAnalyses()
    for analysis in analyses:
        if dettached_states:
            if api.get_review_status(analysis) in dettached_states:
                detached_count += 1
                continue
        if not api.is_active(analysis):
            return False
        if not wasTransitionPerformed(analysis, transition_id):
            return False

    if detached_count == len(analyses):
        # If all analyses are in a detached state, it means that the
        # condition of at least having one child for which the
        # transition is performed is not satisfied so return False
        return False
    return True


def guard_submit(obj):
    """Returns if 'submit' transition can be applied to the worksheet passed in.
    By default, the target state for the 'submit' transition for a worksheet is
    'to_be_verified', so this guard returns true if all the analyses assigned
    to the worksheet have already been submitted. Those analyses that are in a
    non-valid state (cancelled, inactive) are dismissed in the evaluation, but
    at least one analysis must be in an active state (and submitted) for this
    guard to return True. Otherwise, always returns False.
    Note this guard depends entirely on the current status of the children.
    """
    detached = ['rejected', 'retracted']
    return _children_are_ready(obj, 'submit', dettached_states=detached)


def guard_retract(worksheet):
    """Return whether the transition retract can be performed or not to the
    worksheet passed in. Since the retract transition from worksheet is a
    shortcut to retract transitions from all analyses the worksheet contains,
    this guard only returns True if retract transition is allowed for all
    analyses the worksheet contains
    """
    analyses = worksheet.getAnalyses()
    detached = ['rejected', 'retracted']
    num_detached = 0
    for analysis in analyses:
        if api.get_workflow_status_of(analysis) in detached:
            num_detached += 1
        elif not isTransitionAllowed(analysis, "retract"):
            return False
    return analyses and num_detached < len(analyses) or False


def guard_verify(obj):
    """Returns True if 'verify' transition can be applied to the Worksheet
    passed in. This is, returns true if all the analyses assigned
    have already been verified. Those analyses that are in an inactive state
    (cancelled, inactive) are dismissed, but at least one analysis must be in
    an active state (and verified), otherwise always return False.
    Note this guard depends entirely on the current status of the children
    :returns: true or false
    """
    dettached = ['rejected', 'retracted']
    return _children_are_ready(obj, 'verify', dettached_states=dettached)


def guard_rollback_to_open(worksheet):
    """Return whether 'rollback_to_receive' transition can be performed or not
    """
    for analysis in worksheet.getAnalyses():
        if api.get_review_status(analysis) in ["assigned"]:
            return True
    return False


def guard_remove(worksheet):
    """Return whether the workflow can be removed. Returns true if the worksheet
    does not contain any analysis
    """
    if worksheet.getAnalyses():
        return False
    return True
