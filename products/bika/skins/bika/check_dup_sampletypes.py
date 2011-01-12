msgs = []
counter = 0
prices = {}
vats = {}
totalprices = {}

old_title = None
old_a = None
msgs.append("('Duplicate Sample types'),")
for a in context.portal_catalog(portal_type='SampleType',
                                sort_on="sortable_title"):
    new_title = a.Title
    if new_title:
        if new_title == old_title:
            msgs.append('title: %s' %( new_title))
        old_title = new_title

msgs.append("('OK'),")

# return all the messages
stuff = ""
for m in msgs:
    stuff = "%s\n%s" %(stuff, m)
return stuff

