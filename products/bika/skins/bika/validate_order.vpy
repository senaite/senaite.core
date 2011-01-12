## Controller Python Script "validate_order"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates order add and edit form

rc = context.reference_catalog
def missing(field):
    message=context.translate('message_input_required', default='Input is required but no input given.', domain='bika')
    state.setError(field, message, 'ar_form_input_required')

if context.REQUEST.form.has_key('labproducts'):
    labproducts = context.REQUEST.form['labproducts']
    amounts = labproducts.values()
    amounts.sort()
    if amounts[-1] == '0':
        missing('Order items') 
else:
    missing('Order items')

if state.getErrors():
    message=context.translate('message_correct_errors', default='Please correct the indicated errors', domain='bika')
    return state.set(
        status='failure',
        portal_status_message=message
    )
else:
    message=context.translate('message_order_created', default='The order was successfully created', domain='bika')
    return state.set(
        portal_status_message=message)
