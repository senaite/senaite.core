## Script (Python) "find_client_folder_for_member"
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

for obj in context.clients.objectValues():
    if member.id in obj.users_with_local_role('Owner'):
        return obj

return None
