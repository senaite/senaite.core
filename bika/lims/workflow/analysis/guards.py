from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from bika.lims.workflow import doActionFor
from bika.lims.workflow import isBasicTransitionAllowed

from plone.api.portal import get_tool


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
