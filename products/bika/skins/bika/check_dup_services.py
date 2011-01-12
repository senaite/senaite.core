msgs = []
counter = 0
prices = {}
vats = {}
totalprices = {}

old_title = None
old_a = None
msgs.append("('Duplicate titles'),")
for a in context.portal_catalog(portal_type='AnalysisService',
                                sort_on="sortable_title"):
    new_title = a.Title
    if new_title:
        if new_title == old_title:
            msgs.append('title: %s' %( new_title))
        old_title = new_title

old_ikey = None
old_a = None
msgs.append("('Duplicate instrument keywords'),")
for a in context.portal_catalog(portal_type='AnalysisService',
                                sort_on="getInstrumentKeyword"):
    as = a.getObject()
    ikey = as.getInstrumentKeyword()
    if ikey:
        if ikey == old_ikey:
            msgs.append('instrument key: %s title1: %s title2: %s' %( as.getInstrumentKeyword(), old_a.Title, as.Title()))
    old_ikey = ikey
    old_a = a


old_akey = None
old_a = None
msgs.append("('Duplicate analysis keywords'),")
for a in context.portal_catalog(portal_type='AnalysisService',
                                sort_on="getAnalysisKey"):
    as = a.getObject()
    akey = as.getAnalysisKey()
    if akey:
        if akey == old_akey:
            msgs.append('instrument key: %s title1: %s title2: %s' %( as.getAnalysisKey(), old_a.Title, as.Title()))
    old_akey = akey
    old_a = a

msgs.append("('OK'),")

# return all the messages
stuff = ""
for m in msgs:
    stuff = "%s\n%s" %(stuff, m)
return stuff

