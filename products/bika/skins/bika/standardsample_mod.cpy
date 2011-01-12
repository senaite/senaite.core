## Controller Python Script "standardsample_mod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Modify standard sample
##
req = context.REQUEST.form

came_from = req['came_from']
description = req['StandardDescription']

cataloguenumber = req['CatalogueNumber']
lotnumber = req['LotNumber']

if req['StandardStock'] == 'None':
    stock = None
else:
    stock = req['StandardStock']

if req['StandardManufacturer'] == 'None':
    manufacturer = None
else:
    manufacturer = req['StandardManufacturer']

if req['DateSampled'] != '':
    in_date = req['DateSampled'][:10]
    try:
        date_sampled = DateTime(in_date)
    except:
        date_sampled = None

date_received = None
if req['DateReceived'] != '':
    in_date = req['DateReceived'][:10]
    try:
        date_received = DateTime(in_date)
    except:
        date_received = None

date_opened = None
if req['DateOpened'] != '':
    in_date = req['DateOpened'][:10]
    try:
        date_opened = DateTime(in_date)
    except:
        date_opened = None

expiry_date = None
if req['ExpiryDate'] != '':
    in_date = req['ExpiryDate'][:10]
    try:
        expiry_date = DateTime(in_date)
    except:
        expiry_date = None

results = {}
for key, value in context.REQUEST.form.items():
    if not key.startswith('spec'):
        continue

    # copy value so that we can manipulate it
    value = value.copy()

    uid = key.split('.')[-1]
    results[uid] = {}
    results[uid]['service'] = uid
    results[uid]['result'] = value['result']
    results[uid]['min'] = value['min']
    results[uid]['max'] = value['max']

specs = []
result_keys = results.keys()
for key in result_keys:
    specs.append(results[key])

if came_from == 'edit':
    uid = req['StandardSampleUID']
    rc = context.reference_catalog
    ss = rc.lookupObject(uid)
    ss_id = ss.getStandardID()
    ss.edit(
        StandardDescription=description,
        CatalogueNumber=cataloguenumber,
        LotNumber=lotnumber,
        StandardStock=stock,
        StandardManufacturer=manufacturer,
        DateSampled=date_sampled,
        DateReceived=date_received,
        DateOpened=date_opened,
        ExpiryDate=expiry_date,
        Results=specs,
        Notes=req['Notes'],
        )
else:
    ss_id = context.generateUniqueId('StandardSample')
    context.invokeFactory(id=ss_id, type_name='StandardSample')
    ss = context[ss_id]
    ss.edit(
        StandardID=ss_id,
        StandardDescription=description,
        CatalogueNumber=cataloguenumber,
        LotNumber=lotnumber,
        StandardStock=stock,
        StandardManufacturer=manufacturer,
        DateSampled=date_sampled, 
        DateReceived=date_received,
        DateOpened=date_opened,
        ExpiryDate=expiry_date, 
        Results=specs,
        Notes=req['Notes'],
        )

ss.reindexObject()


from Products.CMFPlone import transaction_note
if came_from == 'edit':
    transaction_note('Standard Sample modified successfully')
    message=context.translate('message_modified', default='${ss_id} was successfully modified', mapping={'ss_id': ss_id}, domain='bika')
else:
    transaction_note('Standard Sample created successfully')
    message=context.translate('message_added', default='${ss_id} was successfully added', mapping={'ss_id': ss_id}, domain='bika')


return state.set(portal_status_message=message)
