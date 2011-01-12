## Script (Python) "get_userlist"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get uid and name of all users who can submit ARs
##

## Client contacts done seperately to lab staff
## to avoid clients seeing each other's contacts

mtool = context.portal_membership

pairs = []

labusers = mtool.searchForMembers(roles=['Manager', 'LabManager', 'LabClerk', 'LabTechnician'])
for member in labusers:
   uid = member.getId()
   fullname = member.getProperty('fullname')
   if fullname is None:
      fullname = ''
   if fullname == '':
      fullname = uid
   pairs.append((uid, fullname)) 

contacts = context.portal_catalog(portal_type='Contact')
for contact in contacts:
   uid = contact.getObject().getUsername()
   fullname = contact.Title
   if uid:
      pairs.append((uid, fullname)) 

mydict1 = {}
mydict2 = {}
x = 0
for uid, fullname in pairs:
   mydict1[uid] = fullname
   x = x + 1
   uniquename = fullname + str(x)
   mydict2[uniquename] = uid
 
uniquenames = mydict2.keys()
uniquenames.sort()
newlist = []
for uniquename in uniquenames:
   uid = mydict2[uniquename]
   fullname = mydict1[uid]
   newlist.append([uid, fullname])
return newlist

