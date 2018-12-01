# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims import workflow as wf


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

    # Cannot assign if the analysis has a worksheet assigned already
    if analysis.getWorksheet():
        return False

    # Cannot assign if user does not have permissions to manage worksheets
    return user_can_manage_worksheets()


def guard_unassign(analysis):
    """Return whether the transition "unassign" can be performed or not
    """
    # Cannot unassign if the analysis is not assigned to any worksheet
    if not analysis.getWorksheet():
        return False

    # Cannot unassign if user does not have permissions to manage worksheets
    return user_can_manage_worksheets()


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

    # Cannot submit if attachment not set, but is required
    if not analysis.getAttachment():
        if analysis.getAttachmentOption() == 'r':
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
        if not user_has_super_roles():
            # Cannot submit if unassigned
            if not analysis.getAnalyst():
                return False
            # Cannot submit if assigned analyst is not the current user
            if analysis.getAnalyst() != api.get_current_user().getId():
                return False

    # Cannot submit unless all dependencies are submitted or can be submitted
    dependencies = analysis.getDependencies()
    return is_transition_allowed_or_performed(dependencies, "submit")


def guard_multi_verify(analysis):
    """Return whether the transition "multi_verify" can be performed or not
    The transition multi_verify will only take place if multi-verification of
    results is enabled.
    """
    # Cannot multiverify if there is only one remaining verification
    remaining_verifications = analysis.getNumberOfRemainingVerifications()
    if remaining_verifications <= 1:
        return False

    # Cannot verify if the user submitted and self-verification is not allowed
    if was_submitted_by_current_user(analysis):
        if not analysis.isSelfVerificationEnabled():
            return False

    # Cannot verify if the user verified and multi verification is not allowed
    if was_verified_by_current_user(analysis):
        if not is_multi_verification_allowed(analysis):
            return False

    # Cannot verify if the user was last verifier and consecutive verification
    # by same user is not allowed
    if current_user_was_last_verifier(analysis):
        if not is_consecutive_multi_verification_allowed(analysis):
            return False

    # Cannot verify unless all dependencies are verified or can be verified
    dependencies = analysis.getDependencies()
    transitions = ["verify", "multi_verify"]
    return is_transition_allowed_or_performed(dependencies, transitions)


def guard_verify(analysis):
    """Return whether the transition "verify" can be performed or not
    """
    # Cannot verify if the number of remaining verifications is > 1
    remaining_verifications = analysis.getNumberOfRemainingVerifications()
    if remaining_verifications > 1:
        return False

    # Cannot verify if the user submitted and self-verification is not allowed
    if was_submitted_by_current_user(analysis):
        if not analysis.isSelfVerificationEnabled():
            return False

    # Cannot verify unless dependencies have been verified or can be verified
    if analysis.getNumberOfRequiredVerifications() <= 1:
        dependencies = analysis.getDependencies()
        return is_transition_allowed_or_performed(dependencies, "verify")

    # This analysis has multi-verification enabled
    # Cannot verify if the user verified and multi verification is not allowed
    if was_verified_by_current_user(analysis):
        if not is_multi_verification_allowed(analysis):
            return False

    # Cannot verify if the user was last verifier and consecutive verification
    # by same user is not allowed
    if current_user_was_last_verifier(analysis):
        if not is_consecutive_multi_verification_allowed(analysis):
            return False

    # Cannot verify unless all dependencies are verified or can be verified
    dependencies = analysis.getDependencies()
    transitions = ["verify", "multi_verify"]
    return is_transition_allowed_or_performed(dependencies, transitions)


def guard_retract(analysis):
    """ Return whether the transition "retract" can be performed or not
    """
    # Cannot retract if there are dependents that cannot be retracted
    if not is_transition_allowed(analysis.getDependents(), "retract"):
        return False

    # Cannot retract if all dependencies have been verified
    return not was_transition_performed(analysis.getDependencies(), "verify")


def guard_reject(analysis):
    """Return whether the transition "reject" can be performed or not
    """
    # Cannot reject if there are dependents that cannot be rejected
    return is_transition_allowed(analysis.getDependents(), "reject")


def guard_publish(analysis):
    """Return whether the transition "publish" can be performed or not. Returns
    True only when the Analysis Request the analysis belongs to is in published
    state. Otherwise, returns False.
    """
    return api.get_workflow_status_of(analysis.getRequest()) == "published"


def user_can_manage_worksheets():
    """Return whether the current user has privileges to manage worksheets
    """
    if not api.get_setup().getRestrictWorksheetManagement():
        # There is no restriction, everybody can manage worksheets
        return True

    # Only Labmanager and Manager roles can manage worksheets
    return user_has_super_roles()


def user_has_super_roles():
    """Return whether the current belongs to superuser roles
    """
    member = api.get_current_user()
    super_roles = ["LabManager", "Manager"]
    diff = filter(lambda role: role in super_roles, member.getRoles())
    return len(diff) > 0


def was_submitted_by_current_user(analysis):
    """Returns whether the analysis was submitted by current user or not
    """
    return analysis.getSubmittedBy() == api.get_current_user().getId()


def was_verified_by_current_user(analysis):
    """Returns whether the analysis was verified by current user or not
    """
    return api.get_current_user().getId() in analysis.getVerificators()


def current_user_was_last_verifier(analysis):
    """Returns whether the current user was the last verifier or not
    """
    verifiers = analysis.getVerificators()
    return verifiers and verifiers[:-1] == api.get_current_user().getId()


def is_consecutive_multi_verification_allowed(analysis):
    """Returns whether multiple verification and consecutive verification is
    allowed or not"""
    multi_type = api.get_setup().getTypeOfmultiVerification()
    return multi_type != "self_multi_not_cons"


def is_multi_verification_allowed(analysis):
    """Returns whether multi verification is allowed or not
    """
    multi_type = api.get_setup().getTypeOfmultiVerification()
    return multi_type != "self_multi_disabled"


def is_transition_allowed(analyses, transition_id):
    """Returns whether all analyses can be transitioned or not
    """
    if not analyses:
        return True
    if not isinstance(analyses, list):
        return is_transition_allowed([analyses], transition_id)
    for analysis in analyses:
        if not wf.isTransitionAllowed(analysis, transition_id):
            return False
    return True


def was_transition_performed(analyses, transition_id):
    """Returns whether all analyses were transitioned or not
    """
    if not analyses:
        return False
    if not isinstance(analyses, list):
        return was_transition_performed([analyses], transition_id)
    for analysis in analyses:
        if not wf.wasTransitionPerformed(analysis, transition_id):
            return False
    return True


def is_transition_allowed_or_performed(analyses, transition_ids):
    """Return whether all analyses can be transitioned or all them were
    transitioned.
    """
    if not analyses:
        return True
    if not isinstance(analyses, list):
        return is_transition_allowed_or_performed([analyses], transition_ids)
    if not isinstance(transition_ids, list):
        return is_transition_allowed_or_performed(analyses, [transition_ids])

    for transition_id in transition_ids:
        for analysis in analyses:
            if not wf.isTransitionAllowed(analysis, transition_id):
                if not wf.wasTransitionPerformed(analysis, transition_id):
                    return False
    return True
