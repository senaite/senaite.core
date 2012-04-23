## Script (Python) "guard_retract_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from bika.lims import Retract

workflow = context.portal_workflow
checkPermission = context.portal_membership.checkPermission

# Can't do anything to the object if it's cancelled
if workflow.getInfoFor(context, 'cancellation_state', 'active') == "cancelled":
    return False

if checkPermission(Retract, context):
    return True

if context.portal_type == "AnalysisRequest":

    # Allow automatic retract (Disregard permission)
    # if any analysis is 'sample_due' or 'sample_received'.
    for analysis in context.getAnalyses(full_objects = True):
        review_state = workflow.getInfoFor(analysis, 'review_state')
        if review_state in ('sample_due', 'sample_received'):
            return True

if context.portal_type == "Worksheet":

    # Allow automatic retract if any analysis is 'sample_received'
    # or any duplicate or reference analysis is 'assigned'.
    for analysis in context.getAnalyses():
        review_state = workflow.getInfoFor(analysis, 'review_state')
        if review_state in ('sample_received', 'assigned'):
            return True

return False
