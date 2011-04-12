## Script (Python) "member_is_client"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Check if member is client
##

# this is used in actions
# so it needs to be a fs python script.

groups_tool=context.portal_groups
membership_tool=context.portal_membership
member = membership_tool.getAuthenticatedMember()
member_groups = [groups_tool.getGroupById(group.id).getGroupName() 
                 for group in groups_tool.getGroupsByUserId(member.id)]

return 'clients' in member_groups
