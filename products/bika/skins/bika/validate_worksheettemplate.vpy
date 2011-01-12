## Controller Python Script "validate_worksheettemplate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates worksheet templates

def missing(field):
    message=context.translate('message_input_required', default='Input is required but no input given.', domain='bika')
    state.setError(field, message, 'ar_form_input_required')

req = context.REQUEST.form
types = req['Type']
num_positions = req['NoOfPositions']
num_positions= int(num_positions)
if num_positions > len(types):
    old_positions = len(types)
else:
    old_positions = num_positions
    


# if reset positions, just flatten the keys for the render - no validation
reset = False
if req.has_key('form.button.more'):
    reset = True

dups = req['SubtypeDup']

if not reset:
    if req['Title'] == '':
        missing('Title')

    if not req.has_key('Service'):
        missing('Service')
        
    for i in range(old_positions):
        if types[i] == 'd':

            if types[int(dups[i]) - 1] != 'a':
                error_field = 'Duplicate analysis (%s)' %(i + 1)
                state.setError(error_field, 'may only apply to a real analysis')


if (state.getErrors() or reset):
    ssts = req['SubtypeSST']
    rows = []
    for i in range(old_positions):
        if (types[i] == 'c') or (types[i] == 's') or (types[i] == 'b'):
            subtype = ssts[i]
        elif types[i] == 'd':
            subtype = dups[i]
        else:
            subtype = ''
        
        rows.append({'pos': i+1,
                     'type':types[i],
                     'sub': subtype})

    context.REQUEST.set('Rows', rows)
    context.REQUEST.set('NoOfPositions', num_positions)

if reset:
    return state.set(status='failure')
elif state.getErrors():
    message=context.translate('message_correct_errors', default='Please correct the indicated errors', domain='bika')
    return state.set(
        status='failure',
        portal_status_message=message
    )
else:
    message=context.translate('message_worksheettemplate_created', default='The worksheet template was successfully created', domain='bika')
    return state.set(
        portal_status_message=message)
