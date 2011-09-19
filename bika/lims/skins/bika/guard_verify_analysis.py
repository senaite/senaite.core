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
    # Only transition to 'verified' if all dependencies are at least there.
    for d in context.getDependencies():
        review_state = wf_tool.getInfoFor(d, 'review_state')
        if review_state in ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified',):
            return False
    return True
elif context.portal_type == 'AnalysisRequest':
    return True
