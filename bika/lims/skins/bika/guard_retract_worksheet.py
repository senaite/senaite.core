## Script (Python) "guard_retract_worksheet"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##

wf_tool = context.portal_workflow

checkPermission = context.portal_membership.checkPermission
if checkPermission('Retract', context):
    return True
else:
    # Allow automatic retract if any analysis is 'sample_received'.
    for analysis in context.getAnalyses(full_objects = True):
        review_state = wf_tool.getInfoFor(analysis, 'review_state')
        if review_state == 'sample_received':
            return True
    return False
