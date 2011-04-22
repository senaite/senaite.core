## Script (Python) "guard_retract_sample"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
membership_tool=context.portal_membership
member = membership_tool.getAuthenticatedMember()

wf_tool = context.portal_workflow
review_state = wf_tool.getInfoFor(context, 'review_state', '')
if review_state != 'assigned' and \
        not ('LabManager' in member.getRoles() or 
             'Manager' in member.getRoles()):
    return 0

return 1
