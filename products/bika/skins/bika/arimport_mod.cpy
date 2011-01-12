## Controller Python Script "arimport_mod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Modify arimport
##
from DateTime import DateTime
req = context.REQUEST.form
rc = context.reference_catalog
came_from = req['came_from']

uid = req['ARImportUID']
arimport = rc.lookupObject(uid)
arimport.edit(
    ClientID= getattr(context.REQUEST, 'ClientID', None),
    ClientName=getattr(context.REQUEST, 'ClientName', None),  
    ClientPhone=getattr(context.REQUEST, 'ClientPhone', None),
    ClientFax=getattr(context.REQUEST, 'ClientFax', None),
    ClientAddress=getattr(context.REQUEST, 'ClientAddress', None),  
    ClientCity=getattr(context.REQUEST, 'ClientCity', None),  
    ClientEmail=getattr(context.REQUEST, 'ClientEmail', None),  
    OrderID=getattr(context.REQUEST, 'OrderID', None),  
    QuoteID=getattr(context.REQUEST, 'QuoteID', None),  
    SamplePoint=getattr(context.REQUEST, 'SamplePoint', None),  
    CCEmails=getattr(context.REQUEST, 'CCEmails', None),  
    Temperature=getattr(context.REQUEST, 'Temperature', None),  
)
if req.has_key('Contact'):
    if req['Contact'] == 'None':
        contact_uid = None
    else:
        contact_uid = req['Contact']
        contact = rc.lookupObject(contact_uid)
        arimport.edit(Contact=contact_uid,
                      ContactName=contact.Title())
if req.has_key('CCContact'):
    if req['CCContact'] == 'None':
        cccontact_uid = None
        cccontact_id = None
    else:
        cccontact_uid = req['CCContact']
        cccontact_id = None
    arimport.edit(CCContact=cccontact_uid,
                  CCContactID=cccontact_id)

# arimport items
for key, value in req.items():
    if not key.startswith('item'):
        continue

    # copy value so that we can manipulate it
    value = value.copy()

    uid = key.split('.')[1]
    arimportitem = rc.lookupObject(uid)


    clientref = None
    clientremarks = None
    clientsid = None
    sampledate = None
    sampletype = None
    containers = None
    profile1 = None
    profile2 = None
    analysis1 = None
    analysis2 = None
    analysis3 = None
    if value.has_key('ClientRef'):
        clientref = value['ClientRef']
    if value.has_key('ClientRemarks'):
        clientremarks = value['ClientRemarks']
    if value.has_key('ClientSid'):
        clientsid = value['ClientSid']
    if value.has_key('SampleDate'):
        sampledate = value['SampleDate']
    if value.has_key('SampleType'):
        sampletype = value['SampleType']
    if value.has_key('NoContainers'):
        containers = value['NoContainers']
    profiles = []
    for i in range(1,3):
        if value.has_key('Profile%s' %i):
            profiles.append(value['Profile%s' % i])

    analyses = []
    for i in range(1,4):
        if value.has_key('Analysis%s' %i):
            analyses.append(value['Analysis%s' % i])
    
    arimportitem.edit(
        ClientRef=clientref, 
        ClientRemarks=clientremarks, 
        ClientSid=clientsid, 
        SampleDate=sampledate, 
        SampleType=sampletype,
        NoContainers=containers, 
        AnalysisProfile=profiles,
        Analyses=analyses,
    )
    arimportitem.reindexObject()


if arimport.getImportOption() == 's':
    valid_batch = context.validate_arimport_s(arimport)
else:
    valid_batch = context.validate_arimport_c(arimport)

arimport.reindexObject()
batchname = arimport.Title()

from Products.CMFPlone import transaction_note
transaction_note('ARImport modified successfully')
message=context.translate('message_arimport_edited', default='ARImport ${batchname} was successfully modified', mapping={'batchname': batchname}, domain='bika')

return state.set(portal_status_message=message)

