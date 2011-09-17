## Script (Python) "guard_submit_analysis"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

wf_tool = context.portal_workflow

analyses = ['Analysis', 'DuplicateAnalysis', 'ReferenceAnalysis']

if context.portal_type in analyses:
    return True
elif context.portal_type == 'AnalysisRequest':
    # Only transition to 'to_be_verified' if all analyses are at least there.
    for a in context.objectValues('Analysis'):
        review_state = wf_tool.getInfoFor(a, 'review_state', '')
        if review_state in ('sample_due', 'sample_received', 'attachment_due'):
            return False
    return True
