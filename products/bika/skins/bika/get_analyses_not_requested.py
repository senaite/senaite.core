## Script (Python) "get_analyses_not_requested"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get requested analyses
##
wf_tool = context.portal_workflow
result = []
for analysis in context.getAnalyses():
    if wf_tool.getInfoFor(analysis, 'review_state', ''
        ) == 'not_requested':
        result.append(analysis)

return result
