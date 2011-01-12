## Controller Python Script "validate_standardsample"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates standard sample add and edit form

rc = context.reference_catalog
def missing(field):
    message=context.translate('message_input_required', default='Input is required but no input given.', domain='bika')
    state.setError(field, message, 'ar_form_input_required')

req = context.REQUEST.form
if req['StandardDescription'] == '':
    missing('Title')

if req['StandardStock'] != 'None':
    stock = req['StandardStock']

if req.has_key('Service'):
    services = req['Service']
else:
    services = []
    missing('Analyses')


date_sampled = None
if req['DateSampled'] != '':
    in_date = req['DateSampled'][:10]
    try:
        date_sampled = DateTime(in_date)
    except:
        error_key = 'Date sampled' 
        state.setError(error_key, ' %s is not a valid date' %in_date)

expiry_date = None
if req['ExpiryDate'] != '':
    in_date = req['ExpiryDate'][:10]
    if in_date != '0000/00/00':
        try:
            expiry_date = DateTime(in_date)
        except:
            error_key = 'Expiry date'
            state.setError(error_key, '%s is not a valid date' %in_date)
    

if not state.getErrors():
    if (expiry_date and date_sampled) and (expiry_date < date_sampled):
        error_key = 'Expiry date'
        state.setError(error_key, ' may not be before date sampled')


specced = []
for key, value in context.REQUEST.form.items():
    if not key.startswith('spec'):
        continue

    # copy value so that we can manipulate it
    value = value.copy()

    for k in ('result', 'min', 'max'):
        flat_key = '%s.%s' % (key, k)
        context.REQUEST.set(flat_key, value.get(k))
 
    uid = key.split('.')[-1]
    service = rc.lookupObject(uid)
    specced.append(uid)

    min = None
    max = None
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

unspecced = ''
for service in services:
    if service not in specced:
        service_obj = rc.lookupObject(service)
        if unspecced:
            unspecced += ', '
        unspecced += service_obj.Title()
if unspecced:
    state.setError(unspecced, 'must be specified or deselected')
    
    

if state.getErrors():
    message=context.translate('message_correct_errors', default='Please correct the indicated errors', domain='bika')
    return state.set(
        status='failure',
        portal_status_message=message
    )
else:
    message=context.translate('message_standard_created', default='The standard sample was successfully created', domain='bika')
    return state.set(
        portal_status_message=message)

