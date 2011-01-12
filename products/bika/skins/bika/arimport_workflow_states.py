## Script (Python) "arimport_workflow_states"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get arimport workflow states
##

states_folder = context.portal_workflow.bika_arimport_workflow.states
state_ids = ('imported', 'submitted')
l = []
for state_id in state_ids:
    state = states_folder[state_id]
    l.append( {'id': state.getId(), 'title': state.title} )
return l
