## Script (Python) "get_toggles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=workflow_type
##title=Get toggle categories
##

if workflow_type == 'sample':
    states = context.sample_workflow_states()
elif workflow_type == 'standardsample':
    states = context.standardsample_workflow_states()
elif workflow_type == 'order':
    states = context.order_workflow_states()
elif workflow_type == 'analysisrequest':
    states = context.analysis_workflow_states()
elif workflow_type == 'worksheet':
    states = context.worksheet_workflow_states()
elif workflow_type == 'arimport':
    states = context.arimport_workflow_states()
else:
     states = []

toggles = []
toggle_cats = ({'id':'all', 'title':'All'},)
for cat in toggle_cats:
    toggles.append( {'id': cat['id'], 'title': cat['title']} )
for state in states:
    toggles.append(state)
return toggles
