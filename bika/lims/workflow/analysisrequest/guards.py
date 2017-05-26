from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from bika.lims.workflow import doActionFor
from bika.lims.workflow import isBasicTransitionAllowed
from bika.lims.workflow.analysis import guards as analysis_guards

from plone.api.portal import get_tool


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
    if not isBasicTransitionAllowed(obj):
        return False
    if not obj.getAnalyses(worksheetanalysis_review_state='assigned'):
        return False
    if obj.getAnalyses(worksheetanalysis_review_state='unassigned'):
        return False
    return True


def unassign(obj):
    """Allow or disallow transition depending on our children's states
    """
    if not isBasicTransitionAllowed(obj):
        return False
    if obj.getAnalyses(worksheetanalysis_review_state='unassigned'):
        return True
    if not obj.getAnalyses(worksheetanalysis_review_state='assigned'):
        return True
    return False


def verify(obj):
    """Checks if the verify transition can be performed to the current
    Analysis Request by the current user depending on the user roles, the
    current status of the object and the number of verifications already
    performed. Delegats to analysis.guards.verify
    Returns True if all associated analyses can be verified.
    :returns: true or false
    """
    # Check if the Analysis Request is in a "verifiable" state
    if obj.isVerifiable():
        # Check if the user can verify the Analysis Request
        mtool = get_tool('portal_membersip')
        member = mtool.getAuthenticatedMember()
        if obj.isUserAllowedToVerify(member):
            for an in obj.getAnalyses(full_objects=True):
                if not analysis_guards.verify(an):
                    return False
            return True

    return False
