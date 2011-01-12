## Controller Python Script "validate_analysisservice"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates analysisservice add and edit form

rc = context.reference_catalog
def missing(field):
    message=context.translate('message_input_required', default='Input is required but no input given.', domain='bika')
    state.setError(field, message, 'ar_form_input_required')

req = context.REQUEST.form

analysis_title = req['Title'].strip()
if analysis_title == '':
    missing('Title')
else:
    dup = False
    for as in context.portal_catalog(portal_type='AnalysisService',
                                     sort_on='sortable_title'):
        if cmp(as.Title, analysis_title) < 0:
            continue
        if cmp(as.Title, analysis_title) > 0:
            break

        if cmp(as.Title, analysis_title) == 0:
            if as.UID != context.UID():
                dup = True
                break
    if dup:
        error_key = 'Title'
        state.setError(error_key,
                    '%s is already in use' %analysis_title)

analysis_cat = req['AnalysisCategory']
if analysis_cat == '':
    missing('AnalysisCategory')

analysis_key = req['AnalysisKey'].strip()
if analysis_key == '':
    missing('AnalysisKey')
else:
    dup = False
    for as in context.portal_catalog(portal_type='AnalysisService',
                                     getAnalysisKey=analysis_key):
        if as.UID != context.UID():
            dup = True
            break
    if dup:
        error_key = 'Analysis key'
        state.setError(error_key,
                    '%s is already in use' %analysis_key)

instrument_key = req['InstrumentKeyword'].strip()
if instrument_key != '':
    dup = False
    for as in context.portal_catalog(portal_type='AnalysisService',
                                     getInstrumentKeyword=instrument_key):
        if as.UID != context.UID():
            dup = True
            break
    if dup:
        error_key = 'Instrument key'
        state.setError(error_key,
                    '%s is already in use' %instrument_key)

error_key = 'Uncertainty'
valid_uncertainties = True
uncertainties = {}
for uncertainty in context.REQUEST.get('Uncertainties', []):
    intercept_min = None
    intercept_max = None
    if uncertainty.has_key('delete'):
        continue
    if uncertainty.has_key('intercept_min') \
    and uncertainty.has_key('intercept_max') \
    and uncertainty.has_key('errorvalue'):
        try:
            intercept_min = float(uncertainty['intercept_min'])
        except ValueError:
            valid_uncertainties = False
            state.setError(error_key, 'Min value %s must be numeric' %(uncertainty['intercept_min']))

        try:
            intercept_max = float(uncertainty['intercept_max'])
        except ValueError:
            valid_uncertainties = False
            state.setError(error_key, 'Max value %s must be numeric' %(uncertainty['intercept_max']))

        try:
            errorvalue = float(uncertainty['errorvalue'])
        except ValueError:
            valid_uncertainties = False
            state.setError(error_key, 'Actual value %s must be numeric' %(uncertainty['errorvalue']))
        if valid_uncertainties:
            uncertainties[intercept_min] = intercept_max
    else:
        state.setError(error_key, 'All 3 values required')
    
    mins = uncertainties.keys()
    mins.sort()
    prev_max = None
    for min in mins:
        max = uncertainties[min]
        if min > max:
            state.setError(error_key, 'Min %s must be less than max %s' %(min, max))
        if prev_max:
            if min < prev_max: 
                state.setError(error_key, 'Min %s must be greater than or equal to max %s' %(min, prev_max))
        prev_max = max

if state.getErrors():
    message=context.translate('message_correct_errors', default='Please correct the indicated errors', domain='bika')
    return state.set(
        status='failure',
        portal_status_message=message
    )
else:
    message=context.translate('message_service_created', default='The analysis service was successfully created', domain='bika')
    return state.set(
        portal_status_message=message)

