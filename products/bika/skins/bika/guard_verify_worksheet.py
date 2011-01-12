## Script (Python) "guard_verify_jobcard"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##

# Manager may always verify
checkPermission = context.portal_membership.checkPermission
if checkPermission('Manage portal', context):
    return 1

from AccessControl import getSecurityManager
user_id = getSecurityManager().getUser().getId()
wf_tool = context.portal_workflow

self_submitted = False
for analysis in context.getAnalyses():
    review_state = wf_tool.getInfoFor(analysis, 'review_state')
    if review_state == 'to_be_verified': 
        review_history = wf_tool.getInfoFor(analysis, 'review_history')
        review_history = context.reverseList(review_history)
        for event in review_history:
            if event.get('action') == 'submit':
                if event.get('actor') == user_id:
                    self_submitted = True
                break
        if self_submitted:
            break
if self_submitted:
    return 0
else:
    return 1

