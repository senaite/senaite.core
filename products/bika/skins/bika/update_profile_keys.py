msgs = []
counter = 0
prices = {}
vats = {}
totalprices = {}

for a in context.portal_catalog(portal_type='ARProfile'):
    as = a.getObject()
    as.edit(ProfileKey=as.Title())
    as.reindexObject()
    counter += 1
msgs.append('%s client profiles updated' %(counter))

counter = 0
for a in context.portal_catalog(portal_type='LabARProfile'):
    as = a.getObject()
    as.edit(ProfileKey=as.Title())
    as.reindexObject()
    counter += 1
msgs.append('%s lab profiles updated' %(counter))

msgs.append("('OK'),")

# return all the messages
stuff = ""
for m in msgs:
    stuff = "%s\n%s" %(stuff, m)
return stuff

