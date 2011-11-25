## Script (Python) "guard_retract_worksheet"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##

from bika.lims import Retract

wf_tool = context.portal_workflow

checkPermission = context.portal_membership.checkPermission
if checkPermission(Retract, context):
    return True
else:
    # Allow automatic retract if any analysis is 'sample_received'
    # or any duplicate or reference analysis is 'assigned'.
    for analysis in context.getAnalyses():
        review_state = wf_tool.getInfoFor(analysis, 'review_state')
        if review_state in ('sample_received', 'assigned',):
            return True
    return False
