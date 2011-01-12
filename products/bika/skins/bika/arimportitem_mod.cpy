## Controller Python Script "arimportitem_mod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Modify arimportitem
##
req = context.REQUEST.form
rc = context.reference_catalog

uid = req['ARImportItemUID']
arimportitem = rc.lookupObject(uid)
sample_id = req['SampleName']
arimportitem.edit(
    SampleName=sample_id,
    ClientRef=req['ClientRef'],
    ClientSid=req['ClientSid'],
    SampleDate=req['SampleDate'],
    SampleType=req['SampleType'],
    PickingSlip=req['PickingSlip'],
    OrderID=req['OrderID'],
    ReportDryMatter=req['ReportDryMatter'],
    Analyses=req['Analyses'],
)
arimport = arimportitem.aq_parent
if arimport.getImportOption == 's':
    valid_batch = context.validate_arimport_s(arimport)
else:
    valid_batch = context.validate_arimport_c(arimport)

arimportitem.reindexObject()
arimport.reindexObject()

from Products.CMFPlone import transaction_note
transaction_note('Order modified successfully')
message=context.translate('message_arimport_edited', default='${sample_id} was successfully modified', mapping={'sample_id': sample_id}, domain='bika')

return state.set(portal_status_message=message)

