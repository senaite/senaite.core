## Controller Python Script "analysisspecs_default"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Set client analysis specs to lab defaults
##
req = context.REQUEST.form.items()

if context.REQUEST.form.has_key('form.button.cancel'):
    return state

analysisspecs = []
analysisspec = {}

ids = []
for spec in context.objectValues('AnalysisSpec'):
    ids.append(spec.getId())

if ids:
    status = 'success'
    message = 'All client analysis specifications have been deleted'
    context.manage_delObjects(ids)

for ls_proxy in context. portal_catalog(portal_type='LabAnalysisSpec'):
    ls = ls_proxy.getObject()
    
    as_id = context.generateUniqueId('AnalysisSpec')
    context.invokeFactory(id=as_id, type_name='AnalysisSpec')
    as = context[as_id]
    as.edit(
        SampleType=ls.getSampleType(),
        ResultsRange=ls.getResultsRange(),
        )

return state
