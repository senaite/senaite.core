## Script (Python) "guard_prepublish_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

workflow = context.portal_workflow

# Can't prepublish if cancelled
if workflow.getInfoFor(context, 'cancellation_state', 'active') == "cancelled":
    return False

if context.portal_type == "AnalysisRequest":
    # Only prepublish if any analyses are in 'verified' or 'published' state
    for a in context.getAnalyses(full_objects = False):
        review_state = a.review_state
        if review_state in ('verified', 'published'):
            return True
    return False

