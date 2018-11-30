# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims import workflow as wf


def attach(obj):
    if not wf.isBasicTransitionAllowed(obj):
        return False
    if not obj.getAttachment():
        return obj.getAttachmentOption() != 'r'
    return True


def dependencies_guard(analysis, transition_id):
    """Return whether the transition(s) passed in can be performed or not to
    the dependencies of the analysis passed in
    """
    if isinstance(transition_id, list):
        for transition_id in transition_id:
            if not dependencies_guard(analysis, transition_id):
                return False
        return True

    for dependency in analysis.getDependencies():
        if not wf.isTransitionAllowed(dependency, transition_id):
            if not wf.wasTransitionPerformed(dependency, transition_id):
                return False
    return True


def guard_assign(analysis):
    """Return whether the transition "assign" can be performed or not
    """
    # TODO Workflow - Analysis. Assign guard to return True only in WS.Add?
    #      We need "unassigned" analyses to appear in Worksheet Add analyses.
    #      Hence, it returns True if the analysis has not been assigned to any
    #      worksheet yet. The problem is this can end up (if the 'assign'
    #      transition is displayed in listings other than WS Add Analyses)
    #      with an analysis transitioned to 'assigned' state, but without
    #      a worksheet assigned!. This transition should only be triggered by
    #      content.worksheet.addAnalysis (see that func for more info)

    # Cannot assign if the Sample has not been received
    if not analysis.isSampleReceived():
        return False

    # Check if only LabManager and Manager roles can manage worksheets
    if analysis.bika_setup.getRestrictWorksheetManagement():
        member = api.get_current_user()
        super_roles = ["LabManager", "Manager"]
        if (len(set(super_roles) - set(member.getRoles())) == len(super_roles)):
            # Current user is not a "super-user"
            return False

    # Cannot assign if the analysis has a worksheet assigned already
    if analysis.getWorksheet():
        return False

    return True


def guard_unassign(analysis):
    """Return whether the transition "unassign" can be performed or not
    """
    # Check if only LabManager and Manager roles can manage worksheets
    if analysis.bika_setup.getRestrictWorksheetManagement():
        member = api.get_current_user()
        super_roles = ["LabManager", "Manager"]
        if (len(set(super_roles) - set(member.getRoles())) == len(super_roles)):
            # Current user is not a "super-user"
            return False

    # Cannot unassign if the analysis does not have a worksheet assigned
    return analysis.getWorksheet() and True or False


def guard_cancel(analysis):
    """Return whether the transition "cancel" can be performed or not. Returns
    True only when the Analysis Request the analysis belongs to is in cancelled
    state. Otherwise, returns False.
    """
    return not api.is_active(analysis.getRequest())


def guard_reinstate(analysis):
    """Return whether the transition "reinstate" can be performed or not.
    Returns True only when the Analysis Request the analysis belongs to is in a
    non-cancelled state. Otherwise, returns False.
    """
    return api.is_active(analysis.getRequest())


def guard_submit(analysis):
    """Return whether the transition "submit" can be performed or not
    """
    # Cannot submit without a result
    if not analysis.getResult():
        return False

    # Cannot submit with interims without value
    for interim in analysis.getInterimFields():
        if not interim.get("value", ""):
            return False

    # Check if can submit based on the Analysis Request state
    if IRequestAnalysis.providedBy(analysis):
        point_of_capture = analysis.getPointOfCapture()
        # Cannot submit if the Sample has not been received
        if point_of_capture == "lab" and not analysis.isSampleReceived():
            return False
        # Cannot submit if the Sample has not been sampled
        if point_of_capture == "field" and not analysis.isSampleSampled():
            return False

    # Check if the current user can submit if is not assigned
    if not analysis.bika_setup.getAllowToSubmitNotAssigned():
        member = api.get_current_user()
        super_roles = ["LabManager", "Manager"]
        if (len(set(super_roles) - set(member.getRoles())) == len(super_roles)):
            # Cannot submit if unassigned
            if not analysis.getAnalyst():
                return False
            # Cannot submit if assigned analyst is not the current user
            if analysis.getAnalyst() != member.getId():
                return False

    # Check dependencies (analyses this analysis depends on)
    return dependencies_guard(analysis, "submit")


def guard_multi_verify(analysis):
    """Return whether the transition "multi_verify" can be performed or not
    The transition multi_verify will only take place if multi-verification of
    results is enabled.
    """
    # If there is only one remaining verification, return False
    remaining_verifications = analysis.getNumberOfRemainingVerifications()
    if remaining_verifications <= 1:
        return False

    # Check if the current user is the same who submitted the result
    user_id = api.get_current_user().getId()
    if (analysis.getSubmittedBy() == user_id):
        if not analysis.isSelfVerificationEnabled():
            return False

    # Check if user is the last verifier and consecutive multi-verification is
    # disabled
    verifiers = analysis.getVerificators()
    mv_type = analysis.bika_setup.getTypeOfmultiVerification()
    if verifiers and verifiers[:-1] == user_id \
            and mv_type == "self_multi_not_cons":
        return False

    # Check if user verified before and self multi-verification is disabled
    if user_id in verifiers and mv_type == "self_multi_disabled":
        return False

    # Check dependencies (analyses this analysis depends on)
    return dependencies_guard(analysis, ["verify", "multi_verify"])


def guard_verify(analysis):
    """Return whether the transition "verify" can be performed or not
    """
    # Check if multi-verification
    remaining_verifications = analysis.getNumberOfRemainingVerifications()
    if remaining_verifications > 1:
        return False

    # Check if the current user is the same that submitted the result
    user_id = api.get_current_user().getId()
    if (analysis.getSubmittedBy() == user_id):
        if not analysis.isSelfVerificationEnabled():
            return False

    if analysis.getNumberOfRequiredVerifications() <= 1:
        # Check dependencies (analyses this analysis depends on)
        return dependencies_guard(analysis, "verify")

    # This analysis requires more than one verification
    # Check if user is the last verifier and consecutive multi-verification is
    # disabled
    verifiers = analysis.getVerificators()
    mv_type = analysis.bika_setup.getTypeOfmultiVerification()
    if verifiers and verifiers[:-1] == user_id \
            and mv_type == "self_multi_not_cons":
        return False

    # Check if user verified before and self multi-verification is disabled
    if user_id in verifiers and mv_type == "self_multi_disabled":
        return False

    # Check dependencies (analyses this analysis depends on)
    return dependencies_guard(analysis, ["verify", "multi_verify"])


def guard_retract(analysis):
    """ Return whether the transition "retract" can be performed or not
    """
    # Cannot retract if there are dependents that cannot be retracted
    for dependent in analysis.getDependents():
        if not wf.isTransitionAllowed(dependent, "retract"):
            return False

    # Cannot retract if all dependencies have been verified
    dependencies = analysis.getDependencies()
    if not dependencies:
        return True
    for dependency in dependencies:
        if not wf.wasTransitionPerformed(dependency, "verify"):
            return True

    return False


def guard_reject(analysis):
    """Return whether the transition "reject" can be performed or not
    """
    # Cannot reject if there are dependents that cannot be rejected
    for dependent in analysis.getDependents():
        if not wf.isTransitionAllowed(dependent, "reject"):
            return False

    return True


def guard_publish(analysis):
    """Return whether the transition "publish" can be performed or not. Returns
    True only when the Analysis Request the analysis belongs to is in published
    state. Otherwise, returns False.
    """
    return api.get_workflow_status_of(analysis.getRequest()) == "published"
