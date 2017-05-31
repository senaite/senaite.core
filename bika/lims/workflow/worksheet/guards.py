from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from bika.lims.workflow import doActionFor
from bika.lims.workflow import getCurrentState
from bika.lims.workflow import isActive
from bika.lims.workflow import isBasicTransitionAllowed
from bika.lims.workflow import wasTransitionPerformed
from bika.lims.workflow.analysis import guards as analysis_guards

from plone.api.portal import get_tool


def verify(obj):
    """Returns True if 'verify' transition can be applied to the Worksheet
    passed in. This is, returns true if all the analyses assigned
    have already been verified. Those analyses that are in an inactive state
    (cancelled, inactive) are dismissed, but at least one analysis must be in
    an active state (and verified), otherwise always return False.
    Note this guard depends entirely on the current status of the children
    :returns: true or false
    """
    analyses = obj.getAnalyses()
    invalid = 0
    for an in analyses:
        # The analysis has already been verified?
        if wasTransitionPerformed(an, 'verify'):
            continue

        # Maybe the analysis is in an 'inactive' state?
        if not isActive(an):
            invalid += 1
            continue

        # Maybe the analysis has been rejected or retracted?
        dettached = ['rejected', 'retracted', 'attachment_due']
        status = getCurrentState(an)
        if status in dettached:
            invalid += 1
            continue

        # At this point we can assume this analysis is an a valid state and
        # could potentially be verified, but the Worksheet can only be
        # verified if all the analyses have been transitioned to verified
        return False

    # Be sure that at least there is one analysis in an active state, it
    # doesn't make sense to verify a Worksheet if all the analyses that
    # contains are rejected or cancelled!
    return len(analyses) - invalid > 0
