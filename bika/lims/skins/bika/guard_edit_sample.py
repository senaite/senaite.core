## Script (Python) "guard_edit_sample"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

wf_tool = context.portal_workflow

# Note: Used by profiles/default/types/Sample.xml not workflows.

# Can't edit the sample if it's cancelled or any analysis has been verified
if wf_tool.getInfoFor(context, 'cancellation_state') == "cancelled":
    return False
else:
    ars = context.getAnalysisRequests()
    for ar in ars:
        for a in ar.getAnalyses():
            if wf_tool.getInfoFor(a.getObject(), 'review_state') in ('verified', 'published'):
                return False

return True

