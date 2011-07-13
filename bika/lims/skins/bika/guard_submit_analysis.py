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
    return context.getResult() is not None
elif context.portal_type == 'AnalysisRequest':
    # Only transition to 'to_be_verified' if all analyses are in the
    # 'to_be_verified' state and if all analyses have values
    for a in context.objectValues('Analysis'):
        review_state = wf_tool.getInfoFor(a, 'review_state', '')
        if review_state in ('sample_due'):
            return False

        value = a.getResult()
        if (value is None) or (value == ''):
            return False

    return True
