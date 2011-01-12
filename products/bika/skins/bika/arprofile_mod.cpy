## Controller Python Script "arprofile_mod"
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

came_from = req['came_from']
profile=req['ProfileTitle']

if came_from == 'edit':
    uid = req['ARProfileUID']
    rc = context.reference_catalog
    arp = rc.lookupObject(uid)
else:
    arp_id = context.generateUniqueId('ARProfile')
    context.invokeFactory(id=arp_id, type_name='ARProfile')
    arp = context[arp_id]

arp.edit(
    ProfileTitle=profile,
    ProfileKey=req['ProfileKey'],
    Service=req['Service'],
    )

arp.reindexObject()


from Products.CMFPlone import transaction_note
if came_from == 'edit':
    transaction_note('Analysis Request Profile modified successfully')
    message=context.translate('message_arprofile_edited', default='${profile} was successfully modified', mapping={'profile': profile}, domain='bika')
else:
    transaction_note('Analysis Request Profile created successfully')
    message=context.translate('message_arprofile_created', default='${profile} was successfully created', mapping={'profile': profile}, domain='bika')


return state.set(portal_status_message=message)
