## Script (Python) "guard_prepublish_ar"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

wf_tool = context.portal_workflow

# Can't prepublish if AR is cancelled
if wf_tool.getInfoFor(context, 'cancellation_state') == "cancelled":
    return False

# Only prepublish if any analyses are in 'verified' or 'published' state
for a in context.getAnalyses(full_objects = False):
    review_state = a.review_state
    if review_state in ('verified', 'published'):
        return True

return False

