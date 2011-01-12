## Script (Python) "get_analyses_prices"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get analyses and their prices
##
wf_tool = context.portal_workflow
result = {}
for analysis in context.getAnalyses():
    if wf_tool.getInfoFor(analysis, 'review_state', ''
        ) != 'not_requested':
        service = analysis.getService().UID()
        result[service] = {'price': analysis.getPrice(), 
            'total': analysis.getTotalPrice()}

return result
