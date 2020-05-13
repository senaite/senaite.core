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

from plone.memoize.request import cache

from bika.lims import api
from bika.lims import logger
from bika.lims import workflow as wf
from bika.lims.api import security
from bika.lims.interfaces import ISubmitted
from bika.lims.interfaces import IVerified
from bika.lims.interfaces import IWorksheet
from bika.lims.interfaces.analysis import IRequestAnalysis


def is_worksheet_context():
    """Returns whether the current context from the request is a Worksheet
    """
    request = api.get_request()
    parents = request.get("PARENTS", [])
    portal_types_names = map(lambda p: getattr(p, "portal_type", None), parents)
    if "Worksheet" in portal_types_names:
        return True

    # Check if the worksheet is declared in request explicitly
    ws_uid = request.get("ws_uid", "")
    obj = api.get_object_by_uid(ws_uid, None)
    if IWorksheet.providedBy(obj):
        return True

    return False


def guard_initialize(analysis):
    """Return whether the transition "initialize" can be performed or not
    """
    request = analysis.getRequest()
    if request.getDateReceived():
        return True
    return False


def guard_assign(analysis):
    """Return whether the transition "assign" can be performed or not
    """
    # Only if the request was done from worksheet context.
    if not is_worksheet_context():
        return False

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
    # Only if the request was done from worksheet context.
    if not is_worksheet_context():
        return False

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
            analyst = analysis.getAnalyst()
            if not analyst:
                return False
            # Cannot submit if assigned analyst is not the current user
            if analyst != security.get_user_id():
                return False

    # Cannot submit unless all dependencies are submitted or can be submitted
    for dependency in analysis.getDependencies():
        if not is_submitted_or_submittable(dependency):
            return False
    return True


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
    for dependency in analysis.getDependencies():
        if not is_verified_or_verifiable(dependency):
            return False
    return True


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
        for dependency in analysis.getDependencies():
            if not is_verified_or_verifiable(dependency):
                return False
        return True

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
    for dependency in analysis.getDependencies():
        if not is_verified_or_verifiable(dependency):
            return False
    return True


def guard_retract(analysis):
    """ Return whether the transition "retract" can be performed or not
    """
    # Cannot retract if there are dependents that cannot be retracted
    if not is_transition_allowed(analysis.getDependents(), "retract"):
        return False

    dependencies = analysis.getDependencies()
    if not dependencies:
        return True

    # Cannot retract if all dependencies have been verified
    if all(map(lambda an: IVerified.providedBy(an), dependencies)):
        return False

    return True


def guard_retest(analysis, check_dependents=True):
    """Return whether the transition "retest" can be performed or not
    """
    # Retest transition does an automatic verify transition, so the analysis
    # should be verifiable first
    if not is_transition_allowed(analysis, "verify"):
        return False

    # Cannot retest if there are dependents that cannot be retested
    if not is_transition_allowed(analysis.getDependents(), "retest"):
        return False

    return True


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
        if not cached_is_transition_allowed(analysis, transition_id):
            return False
    return True


def _transition_cache_key(fun, obj, action):
    """Cache key generator for the request cache

    This function generates cache keys like this:
    >>> from bika.lims import api
    >>> from zope.annotation.interfaces import IAnnotations
    >>> request = api.get_request()
    >>> IAnnotations(request)
    # noqa: E501
    {'bika.lims.workflow.analysis.guards.check_analysis_allows_transition:3ff02762c70f4a56b1b30c1b74d32bf6-retract': True,
     'bika.lims.workflow.analysis.guards.check_analysis_allows_transition:0390c16ddec14a04b87ff8408e2aa229-retract': True,
     ...
    }
    """
    return "%s-%s" % (api.get_uid(obj), action)


@cache(get_key=_transition_cache_key, get_request="analysis.REQUEST")
def cached_is_transition_allowed(analysis, transition_id):
    """Check if the transition is allowed for the given analysis and cache the
    value on the request.

    Note: The request is obtained by the given expression from the `locals()`,
          which includes the given arguments.
    """
    logger.debug("cached_is_transition_allowed: analyis=%r transition=%s"
                 % (analysis, transition_id))
    if wf.isTransitionAllowed(analysis, transition_id):
        return True
    return False


def is_submitted_or_submittable(analysis):
    """Returns whether the analysis is submittable or has already been submitted
    """
    if ISubmitted.providedBy(analysis):
        return True
    if wf.isTransitionAllowed(analysis, "submit"):
        return True
    return False


def is_verified_or_verifiable(analysis):
    """Returns whether the analysis is verifiable or has already been verified
    """
    if IVerified.providedBy(analysis):
        return True
    if wf.isTransitionAllowed(analysis, "verify"):
        return True
    if wf.isTransitionAllowed(analysis, "multi_verify"):
        return True
    return False
