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

if context.portal_type == 'AnalysisRequest':
    # Only republish if any analyses are in 'published' state 
    for a in context.getAnalyses():
        review_state = wf_tool.getInfoFor(a, 'review_state', '')
        if review_state in ('verified', 'published'):
            return True

return False

