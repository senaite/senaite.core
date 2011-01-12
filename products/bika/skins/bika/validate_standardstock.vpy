## Controller Python Script "validate_standardstock"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates standard stock add and edit form
rc = context.reference_catalog
def missing(field):
    message=context.translate('message_input_required', default='Input is required but no input given.', domain='bika')
    state.setError(field, message, 'ar_form_input_required')

req = context.REQUEST.form
if req['Title'] == '':
    missing('Title')

if not req.has_key('Service'):
    missing('Analyses')

    
date_created = None
if req['DateCreated'] != '':
    in_date = req['DateCreated'][:10]
    try:
        date_created = DateTime(in_date)
    except:
        error_key = 'Date created' 
        state.setError(error_key, ' %s is not a valid date' %in_date)
    
expiry_date = None
if req['ExpiryDate'] != '':
    in_date = req['ExpiryDate'][:10]
    try:
        expiry_date = DateTime(in_date)
    except:
        error_key = 'Expiry date'
        state.setError(error_key, '%s is not a valid date' %in_date)

for key, value in context.REQUEST.form.items():
    if not key.startswith('stock'):
        continue

    # copy value so that we can manipulate it
    value = value.copy()

    for k in ('result', 'min', 'max'):
        flat_key = '%s.%s' % (key, k)
        context.REQUEST.set(flat_key, value.get(k))

    uid = key.split('.')[-1]
    service = rc.lookupObject(uid)

    if (not value.has_key('result') \
     or not value.has_key('min') \
     or not value.has_key('max')):
        state.setError(service.Title(), 'Result, min and max are required')
    else:
        if (value['result'] == '' \
        or value['min'] == '' \
        or value['max'] == ''):
            state.setError(service.Title(), 'Result, min and max are required')
        else:
            try:
                result = float(value['result'])
                min = float(value['min'])
                max = float(value['max'])
            except ValueError:
                state.setError(service.Title(), 'Result, min and max must be numeric')
    if min and max:
        if min > max:
            state.setError(service.Title(), 'Max must be greater than min')
        if result == 0 or result:
            if (min > result) or (result > max):
                state.setError(service.Title(), 'Result must be between min and max')
if state.getErrors():
    message=context.translate('message_correct_errors', default='Please correct the indicated errors', domain='bika')
    return state.set(
        status='failure',
        portal_status_message=message
    )
else:
    message=context.translate('message_changes_saved', default='Your changes have been saved', domain='bika')
    return state.set(
        portal_status_message=message)
