## Controller Python Script "standardstock_mod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Modify standard stock
##
req = context.REQUEST.form

this_uid = req['StandardStockUID']
rc = context.reference_catalog
sst = rc.lookupObject(this_uid)

stocks = {}

for key, value in req.items():
    if not key.startswith('stock'):
        continue

    # copy value so that we can manipulate it
    value = value.copy()

    uid = key.split('.')[-1]
    stocks[uid] = {}
    stocks[uid]['service'] = uid
    stocks[uid]['result'] = value['result']
    stocks[uid]['min'] = value['min']
    stocks[uid]['max'] = value['max']

services = req['Service']
for service in services:
    if not stocks.has_key(service):
        stocks[service] = {'service': service,
                           'result': '',
                           'min': '',
                           'max': ''}

specs = []
stock_keys = stocks.keys()
    
for key in stock_keys:
    specs.append(stocks[key])

sst.edit(
    title=context.REQUEST.form['Title'],
    StandardStockDescription=context.REQUEST.form['Description'],
    DateCreated=context.REQUEST.form['DateCreated'],
    ExpiryDate=context.REQUEST.form['ExpiryDate'],
    Hazardous=context.REQUEST.form['Hazardous'],
    StandardResults=specs,
    )


from Products.CMFPlone import transaction_note
transaction_note('Standard Stock modified successfully')

return state
