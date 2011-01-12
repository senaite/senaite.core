## Script (Python) "get_contact_browser_startup_directory"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
checkPermission = context.portal_membership.checkPermission
clients_folder = context.clients
if checkPermission('listFolderContents', clients_folder):
    return clients_folder.absolute_url()
    
# if we don't have permission we are most probably a client
membership_tool=context.portal_membership
member = membership_tool.getAuthenticatedMember()

for obj in context.clients.objectValues():
    if member.id in obj.users_with_local_role('Owner'):
        return obj.absolute_url()

return context.absolute_url()

