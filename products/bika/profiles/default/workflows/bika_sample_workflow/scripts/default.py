## Script (Python) "default"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_info
##title=
##
# Delegate to action on instance
action_id = state_info['transition'].getId()
prefix = 'workflow_script_' 
method_id = prefix + action_id
method = getattr(state_info['object'], method_id, None)
if method is not None:
    method(state_info)
