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
    revers = obj.getNumberOfRequiredVerifications()
    nmvers = obj.getNumberOfVerifications()
    if revers-numvers <= 1:
        if obj.isVerifiable():
            # Check if the user can verify the Analysis
            mtool = get_tool('portal_membership')
            member = mtool.getAuthenticatedMember()
            return obj.isUserAllowedToVerify(member)

    return False
