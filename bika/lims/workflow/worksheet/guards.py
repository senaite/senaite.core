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
from bika.lims.interfaces import ISubmitted, IVerified
from bika.lims.workflow import isTransitionAllowed


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
    analyses = obj.getAnalyses()
    if not analyses:
        # An empty worksheet cannot be submitted
        return False

    for analysis in obj.getAnalyses():
        # Dismiss analyses that are not active
        if not api.is_active(analysis):
            continue
        # Dismiss analyses that have been rejected or retracted
        if api.get_workflow_status_of(analysis) in ["rejected", "retracted"]:
            continue
        # Worksheet cannot be submitted if there is one analysis not submitted
        if not ISubmitted.providedBy(analysis):
            return False

    return True


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

    analyses = obj.getAnalyses()
    if not analyses:
        # An empty worksheet cannot be verified
        return False

    for analysis in obj.getAnalyses():
        # Dismiss analyses that are not active
        if not api.is_active(analysis):
            continue
        # Dismiss analyses that have been rejected or retracted
        if api.get_workflow_status_of(analysis) in ["rejected", "retracted"]:
            continue
        # Worksheet cannot be verified if there is one analysis not verified
        if not IVerified.providedBy(analysis):
            return False

    return True


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
