## Script (Python) "get_submitted_by"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ar
##title=Determine who submitted analysis results for an ar
##
wf_tool = context.portal_workflow
submitters = []
for analysis in ar.getAnalyses():
    if analysis.getCalcType() == 'dep':
        continue
    review_state = wf_tool.getInfoFor(analysis, 'review_state')
    if review_state == 'to_be_verified': 
        review_history = wf_tool.getInfoFor(analysis, 'review_history')
        review_history = context.reverseList(review_history)
        for event in review_history:
            if event.get('action') == 'submit':
                submitter = event.get('actor')
                if submitter not in submitters:
                    submitters.append(submitter)
return submitters
