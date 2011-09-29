## Script (Python) "guard_retract_ar"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

wf_tool = context.portal_workflow

checkPermission = context.portal_membership.checkPermission
if checkPermission('Retract', context):
    return True
else:
    # Allow automatic retract if any analysis is 'sample_due' or 'sample_received'.
    for analysis in context.getAnalyses(full_objects = True):
        review_state = wf_tool.getInfoFor(analysis, 'review_state')
        if review_state in ('sample_due', 'sample_received'):
            return True
    return False
