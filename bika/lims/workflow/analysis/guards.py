# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.permissions import Unassign
from bika.lims import workflow as wf


def sample(obj):
    """ Returns true if the sample transition can be performed for the sample
    passed in.
    :returns: true or false
    """
    return wf.isBasicTransitionAllowed(obj)

def retract(obj):
    """ Returns true if the sample transition can be performed for the sample
    passed in.
    :returns: true or false
    """
    return wf.isBasicTransitionAllowed(obj)


def receive(obj):
    return wf.isBasicTransitionAllowed(obj)


def publish(obj):
    """ Returns true if the 'publish' transition can be performed to the
    analysis passed in.
    In accordance with bika_analysis_workflow, 'publish'
    transition can only be performed if the state of the analysis is verified,
    so this guard only checks if the analysis state is active: there is no need
    of additional checks, cause the DC Workflow machinery will already take
    care of them.
    :returns: true or false
    """
    return wf.isBasicTransitionAllowed(obj)


def import_transition(obj):
    return wf.isBasicTransitionAllowed(obj)


def attach(obj):
    if not wf.isBasicTransitionAllowed(obj):
        return False
    if not obj.getAttachment():
        return obj.getAttachmentOption() != 'r'
    return True


def assign(obj):
    return wf.isBasicTransitionAllowed(obj)


def unassign(obj):
    """Check permission against parent worksheet
    """
    mtool = getToolByName(obj, "portal_membership")
    if not wf.isBasicTransitionAllowed(obj):
        return False
    ws = obj.getBackReferences("WorksheetAnalysis")
    if not ws:
        return False
    ws = ws[0]
    if wf.isBasicTransitionAllowed(ws):
        if mtool.checkPermission(Unassign, ws):
            return True
    return False


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


def guard_submit(analysis):
    """Return whether the transition "submit" can be performed or not
    """
    # Cannot submit if the analysis is cancelled
    if not api.is_active(analysis):
        return False

    # Cannot submit without a result
    if not analysis.getResult():
        return False

    # Cannot submit with interims without value
    for interim in analysis.getInterimFields():
        if not interim.get("value", ""):
            return False

    # Check if can submit based on the Analysis Request state
    if IRequestAnalysis.providedBy(analysis):
        analysis_request = analysis.getRequest()
        if analysis.getPointOfCapture() == "lab":
            # Cannot submit if the AR has not been received
            if not wf.wasTransitionPerformed(analysis_request, "receive"):
                # TODO Workflow - Analysis. Remove this check as soon as changeWorkflowAction is removed from everywhere!
                if not api.get_workflow_status_of(analysis_request) == "sample_received":
                    return False
        if analysis.getPointOfCapture() == "field":
            # Cannot submit if the AR has not been sampled
            if not wf.wasTransitionPerformed(analysis_request, "sample"):
                # TODO Workflow - Analysis. Remove this check as soon as changeWorkflowAction is removed from everywhere!
                if not api.get_workflow_status_of(analysis_request) in ["sample_due", "sample_received"]:
                    return False

    # Check if the current user can submit if is not assigned
    if not analysis.bika_setup.getAllowToSubmitNotAssigned():
        m_tool = getToolByName(analysis, 'portal_membership')
        member = m_tool.getAuthenticatedMember()
        super_roles = ["LabManager", "Manager"]
        if (len(set(super_roles) - set(member.getRoles())) == len(super_roles)):
            # User does not have a "super-role"
            if not analysis.getAnalyst():
                return False
            if analysis.getAnalyst() != member.getUser().getId():
                return False

    # Check dependencies (analyses this analysis depends on)
    return dependencies_guard(analysis, "submit")


def guard_multi_verify(analysis):
    """Return whether the transition "multi_verify" can be performed or not
    The transition multi_verify will only take place if multi-verification of
    results is enabled.
    """
    if not api.is_active(analysis):
        return False

    # If there is only one remaining verification, return False
    remaining_verifications = analysis.getNumberOfRemainingVerifications()
    if remaining_verifications <= 1:
        return False

    # Check if the current user is the same who submitted the result
    m_tool = getToolByName(analysis, 'portal_membership')
    user_id = m_tool.getAuthenticatedMember().getUser().getId()
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
    # Cannot verify if the analysis is cancelled
    if not api.is_active(analysis):
        return False

    # Check if multi-verification
    remaining_verifications = analysis.getNumberOfRemainingVerifications()
    if remaining_verifications > 1:
        return False

    # Check if the current user is the same that submitted the result
    m_tool = getToolByName(analysis, 'portal_membership')
    user_id = m_tool.getAuthenticatedMember().getUser().getId()
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

