# Script (Python) "misc"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=miscellaneous script
##
count = 0
msgs = []
msg = ''

for p in context.portal_catalog(portal_type="Client"):
    client = p.getObject()
    count += 1


msgs.append('%s read' %count)
# return all the messages
stuff = ''
for m in msgs:
    stuff = '%s\n%s' %(stuff, m)
return stuff
