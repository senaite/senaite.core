from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from bika.lims.workflow import doActionFor
from bika.lims.workflow import isBasicTransitionAllowed


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


def guard_unassign_transition(obj):
    """Allow or disallow transition depending on our children's states
    """
    if not isBasicTransitionAllowed(obj):
        return False
    if obj.getAnalyses(worksheetanalysis_review_state='unassigned'):
        return True
    if not obj.getAnalyses(worksheetanalysis_review_state='assigned'):
        return True
    return False


def guard_verify_transition(obj):
    """
    Checks if the verify transition can be performed to the current
    Analysis Request by the current user depending on the user roles, as
    well as the statuses of the analyses assigned to this Analysis Request
    :returns: true or false
    """
    mtool = getToolByName(obj, "portal_membership")
    # Check if the Analysis Request is in a "verifiable" state
    if obj.isVerifiable():
        # Check if the user can verify the Analysis Request
        member = mtool.getAuthenticatedMember()
        return obj.isUserAllowedToVerify(member)
    return False
