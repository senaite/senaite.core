## Script (Python) "guard_sampled_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##

from DateTime import DateTime
workflow = context.portal_workflow

# False if object is cancelled
if workflow.getInfoFor(context, 'cancellation_state', "active") == "cancelled":
    return False

if context.portal_type == 'AnalysisRequest':

    # False if our SamplingDate is the future
    if context.getSample().getSamplingDate() > DateTime():
        return False

elif context.portal_type == 'Sample':

    # False if our SamplingDate is the future
    if context.getSamplingDate() > DateTime():
        return False

# Always available for Analysis

return True
