## Script (Python) "get_client_for_member"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get associated client for member
##
membership_tool=context.portal_membership
member = membership_tool.getAuthenticatedMember()
for client in context.clients.objectValues():
    if member.id in client.users_with_local_role('Owner'):
        return client
