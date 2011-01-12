## Script (Python) "get_requested_analyses"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get requested analyses
##
wf_tool = context.portal_workflow
result = []
cats = {}
for analysis in context.getAnalyses():
    if wf_tool.getInfoFor(analysis, 'review_state', ''
        ) == 'not_requested':
        continue
    if not cats.has_key(analysis.getService().getCategoryName()):
        cats[analysis.getService().getCategoryName()] = {}
    analyses = cats[analysis.getService().getCategoryName()]
    analyses[analysis.Title()] = analysis
    cats[analysis.getService().getCategoryName()] = analyses
        
cat_keys = cats.keys()
cat_keys.sort(lambda x,y:cmp(x.lower(), y.lower()))

for cat_key in cat_keys:
    analyses = cats[cat_key]
    analysis_keys = analyses.keys()
    analysis_keys.sort(lambda x,y:cmp(x.lower(), y.lower()))
    for analysis_key in analysis_keys:
        result.append(analyses[analysis_key])

return result
