## Script (Python) "order_workflow_states"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get order workflow states
##

states_folder = context.portal_workflow.bika_order_workflow.states
state_ids = ('pending', 'dispatched')
l = []
for state_id in state_ids:
    state = states_folder[state_id]
    l.append( {'id': state.getId(), 'title': state.title} )
return l
