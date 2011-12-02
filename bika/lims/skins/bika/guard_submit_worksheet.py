## Script (Python) "guard_submit_worksheet"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

if not context.getAnalyst():
    return False

# Only transition to 'attachment_due' if all analyses are at least there.
has_analyses = False
wf_tool = context.portal_workflow
for a in context.getAnalyses():
    has_analyses = True
    review_state = wf_tool.getInfoFor(a, 'review_state', '')
    if review_state in ('sample_due', 'sample_received', 'assigned',):
        # Note: referenceanalyses and duplicateanalyses can still have review_state = "assigned".
        return False
if has_analyses:
    return True
else:
    return False



