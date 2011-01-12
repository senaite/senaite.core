## Controller Python Script "worksheettemplate_mod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Modify worksheet template 
##

req = context.REQUEST.form


uid = req['WorksheetTemplateUID']
rc = context.reference_catalog
wst = rc.lookupObject(uid)

types = req['Type'] 
ssts= req['SubtypeSST'] 
dups = req['SubtypeDup'] 
num_positions = len(types)
rows = []
for i in range(0, num_positions):
        if (types[i] == 'c') or (types[i] == 'b'):
            subtype = ssts[i]
        elif types[i] == 'd':
            subtype = dups[i]
        else:
            subtype = ''
        
        rows.append({'pos': i+1,
                     'type':types[i],
                     'sub': subtype})

wst.edit(
    title=req['Title'],
    WorksheetTemplateDescription=req['Description'],
    Row=rows,
    Service=req['Service'],
    )

wst.reindexObject()


from Products.CMFPlone import transaction_note
transaction_note('Worksheet Template modified successfully')

return state
