## Controller Python Script "validate_analysisspec"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates analysis spec add and edit form

rc = context.reference_catalog
def missing(field):
    message=context.translate('message_input_required', default='Input is required but no input given.', domain='bika')
    state.setError(field, message, 'ar_form_input_required')

spec_found = False
st_found = False
came_from = context.REQUEST.form['came_from']
for key, value in context.REQUEST.form.items():
    if came_from == 'add':
        if key.startswith('sampletypes'):
            st_found = True
            continue
    else:
        if key.startswith('SampleType'):
            st_found = True
            continue
        
    if not key.startswith('analysisspec'):
        continue

    spec_found = True
    # copy value so that we can manipulate it
    value = value.copy()

    for k in ('min', 'max', 'error'):
        flat_key = '%s.%s' % (key, k)
        context.REQUEST.set(flat_key, value.get(k))
 
    uid = key.split('.')[-1]
    service = rc.lookupObject(uid)

    if (not value.has_key('min') \
     or not value.has_key('max') \
     or not value.has_key('error')):
        state.setError(service.Title(), 'Min, max and % error are required')
    else:
        try:
            min = float(value['min'])
            max = float(value['max'])
            error = float(value['error'])
            if not (max >= min):
                state.setError(service.Title(), 'Max required to be greater than min')
        except ValueError:
            state.setError(service.Title(), 'Min, max and % error must be numeric')

if not spec_found:
    missing('Analyses')
if not st_found:
    missing('Sample type')

if state.getErrors():
    message=context.translate('message_correct_errors', default='Please correct the indicated errors', domain='bika')
    return state.set(
        status='failure',
        portal_status_message=message
    )
else:
    message=context.translate('message_spec_created', default='The analysis specification was successfully created', domain='bika')
    return state.set(
        portal_status_message=message)
