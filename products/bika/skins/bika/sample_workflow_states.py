## Script (Python) "sample_workflow_states"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get sample workflow states
##

states_folder = context.portal_workflow.bika_sample_workflow.states
state_ids = ('due', 'received', 'expired', 'disposed')
l = []
for state_id in state_ids:
    state = states_folder[state_id]
    l.append( {'id': state.getId(), 'title': state.title} )
return l
