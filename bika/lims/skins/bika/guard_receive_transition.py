## Script (Python) "guard_receive_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from DateTime import DateTime
workflow = context.portal_workflow

# False if object is cancelled
if workflow.getInfoFor(context, 'cancellation_state', "active") == "cancelled":
    return False

if context.portal_type == 'AnalysisRequest':

    # False if our Sample's SamplingDate is the future
    if context.getSample().getSamplingDate() > DateTime():
        return False

    # False if any Field Analyses in any of our sample's ARs have no result.
    for ar in context.getSample().getAnalysisRequests():
        if [a for a in ar.getAnalyses(getPointOfCapture='field')
            if a.getObject().getResult() == '']:
            return False

elif context.portal_type == 'Sample':

    # False if our SamplingDate is the future
    if context.getSamplingDate() > DateTime():
        return False

    # False if any of this Sample's ARs have Field Analyses without results.
    for ar in context.getAnalysisRequests():
        if [a for a in ar.getAnalyses(getPointOfCapture='field')
            if a.getObject().getResult() == '']:
            return False

return True
