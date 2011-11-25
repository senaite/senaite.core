## Script (Python) "guard_verify_analysis"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from bika.lims import VerifyOwnResults

wf_tool = context.portal_workflow

# Can't do anything to the object if it's cancelled
# reference and duplicate analyses don't hapve cancellation_state
if context.portal_type == "Analysis":
    if wf_tool.getInfoFor(context, 'cancellation_state', '') == "cancelled":
        return False

# Check if all dependencies are at least 'verified'.
# reference and duplicate analyses don't happen on services with dependencies
if context.portal_type == "Analysis":
    for d in context.getDependencies():
        review_state = wf_tool.getInfoFor(d, 'review_state')
        if review_state in ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified',):
            return False

checkPermission = context.portal_membership.checkPermission
if checkPermission(VerifyOwnResults, context):
    return True

# Check if submitted by same user.
from AccessControl import getSecurityManager
user_id = getSecurityManager().getUser().getId()

self_submitted = False
review_history = wf_tool.getInfoFor(context, 'review_history')
review_history = context.reverseList(review_history)
for event in review_history:
    if event.get('action') == 'submit':
        if event.get('actor') == user_id:
            self_submitted = True
        break
if self_submitted:
    return False
else:
    return True

