## Controller Python Script "order_mod"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Modify order
##
from DateTime import DateTime
req = context.REQUEST.form

came_from = req['came_from']
products = context.REQUEST.form['labproducts']

rc = context.reference_catalog

if came_from == 'edit':
    # check out just using context, not getting object AVS AVS 
    uid = req['OrderUID']
    order = rc.lookupObject(uid)
    order.edit(
        Contact=context.REQUEST.Contact,
        )
    order.manage_delObjects(ids=context.objectIds('OrderItem'))
    order_id = order.getOrderNumber()
else:
    order_id = context.generateUniqueId('Order')
    context.invokeFactory(id=order_id, type_name='Order')
    order = context[order_id]
    order.edit(
        OrderNumber=order_id,
        OrderDate=DateTime(),
        Contact=context.REQUEST.Contact,
        )

for uid, qty in products.items():
    qty = int(qty)
    if qty <= 0: continue
    labproduct = rc.lookupObject(uid)
    item_id = labproduct.getId()
    order.invokeFactory(id=item_id, type_name='OrderItem')
    item = order[item_id]
    item.edit(
        Product=uid,
        Quantity=qty,
        Price=labproduct.getPrice(),
        VAT=labproduct.getVAT()
    )

order.reindexObject()


from Products.CMFPlone import transaction_note
if came_from == 'edit':
    transaction_note('Order modified successfully')
    message=context.translate('message_order_edited', default='Order ${order_id} was successfully modified', mapping={'order_id': order_id}, domain='bika')
else:
    transaction_note('Order created successfully')
    message=context.translate('message_order_created', default='Order ${order_id} was successfully created', mapping={'order_id': order_id}, domain='bika')


return state.set(portal_status_message=message)

