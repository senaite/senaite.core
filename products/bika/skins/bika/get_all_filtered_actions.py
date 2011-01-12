## Script (Python) "get_all_filtered_actions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=batch
##title=Get all filtered actions
##
# since to_be_verified ars may not be verified by the same person who submitted
# them, this suppresses the verify button for to_be_verified ars, if the first
# in the batch happens to not be able to be verified
action_tool = context.portal_actions
action_ids = []
all_actions = []
for item in batch:
    ar_actions = action_tool.listFilteredActionsFor(item.getObject());
    wf_actions = ar_actions['workflow']
    for action in wf_actions:
        if action['id'] not in action_ids:
            action_ids.append(action['id'])
            all_actions.append(action)

return all_actions
