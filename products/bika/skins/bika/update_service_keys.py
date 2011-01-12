msgs = []
counter = 0
prices = {}
vats = {}
totalprices = {}

for a in context.portal_catalog(portal_type='AnalysisService'):
    as = a.getObject()
    as.edit(InstrumentKeyword=as.Title(),
            AnalysisKey=as.Title())
    as.reindexObject()
    counter += 1



msgs.append('%s analysis services updated' %(counter))
msgs.append("('OK'),")

# return all the messages
stuff = ""
for m in msgs:
    stuff = "%s\n%s" %(stuff, m)
return stuff

