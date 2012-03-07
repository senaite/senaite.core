## Script (Python) "analysis_workflow_states"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get analysis workflow states
##

states_folder = context.portal_workflow.bika_analysis_workflow.states
state_ids = ('to_be_sampled', 'to_be_preserved', 'sample_due', 'sample_received',
             'attachment_due', 'to_be_verified', 'verified', 'published')
l = []
for state_id in state_ids:
    state = states_folder[state_id]
    l.append( {'id': state.getId(), 'title': state.title} )
return l
