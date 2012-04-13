## Script (Python) "cancellation_workflow_states"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get cancellation workflow states
##

state_ids = ('active', 'cancelled')

l = []
for state_id in state_ids:
    state_title = context.portal_workflow.getTitleForStateOnType(state_id,
                    'Analysis')
    l.append( {'id': state_id, 'title': state_title} )
return l
