## Controller Python Script "prefs_group_members_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=groupname, add=[]
##title=Edit group members
##

from Products.CMFPlone import PloneMessageFactory as _

REQUEST=context.REQUEST
group=context.portal_groups.getGroupById(groupname)

for u in add:
    group.addMember(u)
if groupname == 'labmanagers':
    pm = context.portal_membership
    clients = context.clients
    pm.setLocalRoles( obj=clients, member_ids=add,
            member_role='Owner')

context.plone_utils.addPortalMessage(_(u'Changes made.'))
return state
