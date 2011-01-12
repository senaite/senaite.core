## Controller Python Script "labarprofile_mod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Modify analysis profile
##

req = context.REQUEST.form


uid = req['ARProfileUID']
rc = context.reference_catalog
arp = rc.lookupObject(uid)

arp.edit(
    ProfileTitle=req['ProfileTitle'],
    ProfileKey=req['ProfileKey'],
    Service=req['Service'],
    )

arp.reindexObject()


from Products.CMFPlone import transaction_note
transaction_note('Analysis Request Profile modified successfully')

return state
