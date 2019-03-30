## Script (Python) "guard_attach_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

workflow = context.portal_workflow

if context.portal_type == "AnalysisRequest":
    # Allow transition to 'attach'
    # if all analyses are at least to_be_verified
    for a in context.getAnalyses(full_objects=True):
        review_state = workflow.getInfoFor(a, 'review_state')
        if review_state in ('unassigned', 'assigned', 'attachment_due'):
            return False
    return True

if context.portal_type == "Worksheet":
    # Allow transition to 'to_be_verified'
    # if all analyses are at least to_be_verified
    for a in context.getAnalyses():
        review_state = workflow.getInfoFor(a, 'review_state')
        if review_state in ('unassigned', 'assigned', 'attachment_due'):
            # Note: referenceanalyses and duplicateanalysis can
            # still have review_state = "assigned".
            return False

return True
