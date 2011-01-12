## Script (Python) "get_analysis_request_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
wf_tool = context.portal_workflow
actions_tool = context.portal_actions

actions = {}
for analysis in context.getAnalyses():
    review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
    if review_state in ('not_requested', 'to_be_verified', 'verified'):
        a = actions_tool.listFilteredActionsFor(analysis)
        for action in a['workflow']:
            if actions.has_key(action['id']):
                continue
            actions[action['id']] = action

return actions.values()
