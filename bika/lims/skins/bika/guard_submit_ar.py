## Script (Python) "guard_submit_ar"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

wf_tool = context.portal_workflow

# Can't do anything to the object if it's cancelled
if wf_tool.getInfoFor(context, 'cancellation_state') == "cancelled":
    return False

# Only transition to 'attachment_due' if all analyses are at least there.
for a in context.objectValues('Analysis'):
    review_state = wf_tool.getInfoFor(a, 'review_state')
    if review_state in ('sample_due', 'sample_received',):
        return False
return True
