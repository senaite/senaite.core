from bika.lims import logger
from bika.lims.workflow import doActionFor
from bika.lims.workflow import isBasicTransitionAllowed

from plone.api.portal import get_tool


def sample(obj):
    """ Returns true if the sample transition can be performed for the sample
    passed in.
    :returns: true or false
    """
    return isBasicTransitionAllowed(obj)

def retract(obj):
    """ Returns true if the sample transition can be performed for the sample
    passed in.
    :returns: true or false
    """
    return isBasicTransitionAllowed(obj)


def sample_prep(obj):
    return isBasicTransitionAllowed(obj)


def sample_prep_complete(obj):
    return isBasicTransitionAllowed(obj)


def receive(obj):
    return isBasicTransitionAllowed(obj)


def publish(obj):
    return isBasicTransitionAllowed(obj)


def import_transition(obj):
    return isBasicTransitionAllowed(obj)


def attach(obj):
    if not isBasicTransitionAllowed(obj):
        return False
    if not obj.getAttachment():
        return obj.getAttachmentOption() != 'r'
    return True


def assign(obj):
    return isBasicTransitionAllowed(obj)


def unassign(obj):
    """Check permission against parent worksheet
    """
    mtool = get_tool("portal_membership")
    if not isBasicTransitionAllowed(obj):
        return False
    ws = obj.getBackReferences("WorksheetAnalysis")
    if not ws:
        return False
    ws = ws[0]
    if isBasicTransitionAllowed(ws):
        if mtool.checkPermissions(Unassign, ws):
            return True
    return False


def verify(obj):
    """
    Checks if the verify transition can be performed to the Analysis passed in
    by the current user depending on the user roles, the current status of the
    object and the number of verifications already performed.
    :returns: true or false
    """
    nmvers = obj.getNumberOfVerifications()
    if nmvers == 0:
        # No verification has been done yet.
        # The analysis can only be verified it all its dependencies have
        # already been verified
        for dep in obj.getDependencies():
            if not verify(dep):
                return False

    revers = obj.getNumberOfRequiredVerifications()
    if revers - nmvers == 1:
        # All verifications performed except the last one. Check if the user
        # can perform the verification and if so, then allow the analysis to
        # be transitioned to the definitive "verified" state (otherwise will
        # remain in "to_be_verified" until all remmaining verifications - 1 are
        # performed
        mtool = get_tool('portal_membership')
        member = mtool.getAuthenticatedMember()
        return obj.isUserAllowedToVerify(member)

    return False
