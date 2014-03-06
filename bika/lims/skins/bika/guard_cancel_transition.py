## Script (Python) "guard_cancel_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from bika.lims.permissions import CancelAndReinstate

checkPermission = context.portal_membership.checkPermission

if context.portal_type == 'AnalysisRequest':
    for analysis in context.getAnalyses(full_objects = True):
        if not checkPermission(CancelAndReinstate, analysis):
            return False
    return True

elif context.portal_type == 'Sample':
    for ar in context.getAnalysisRequests():
        if not checkPermission(CancelAndReinstate, ar):
            return False
        for analysis in ar.getAnalyses(full_objects = True):
            if not checkPermission(CancelAndReinstate, analysis):
                return False
    return True

return True
