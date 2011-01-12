## Controller Python Script "validate_arprofile"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates analysis profile add and edit form

def missing(field):
    message=context.translate('message_input_required', default='Input is required but no input given.', domain='bika')
    state.setError(field, message, 'ar_form_input_required')

req = context.REQUEST.form
if req.has_key('Service'):
    analyses = req['Service']
else:
    analyses = []
    missing('Analyses')
    
if req['ProfileTitle'] == '':
    missing('Title')
    
profile_key = req['ProfileKey']
if profile_key == '':
    missing('Profile key')
else:
    dup = False
    for pp in context.portal_catalog(portal_type='ARProfile',
                                     getProfileKey=profile_key):
        if pp.UID != context.UID():
            dup = True
            break
    if not dup:
        for pp in context.portal_catalog(portal_type='LabARProfile',
                                        getProfileKey=profile_key):
            if pp.UID != context.UID():
                dup = True
                break
    if dup:
        error_key = 'Profile key'
        state.setError(error_key,
                    '%s is already in use' %profile_key)

if analyses:
    rc = context.reference_catalog
    dependant_services = {}
    for s in context.portal_catalog(portal_type="AnalysisService"):
        service = s.getObject()
        if service.getCalcType() == 'dep':
            dependant_services[service.UID()] = service

    # validate analyses
    for analysis in analyses:
        # validate analysis dependancies
        reqd_analyses = []
        if dependant_services.has_key(analysis):
            this_analysis = dependant_services[analysis]
            required = context.get_analysis_dependancies(this_analysis)
            reqd_analyses = required['uids']
        reqd_titles = ''
        for reqd in reqd_analyses:
            if (reqd not in analyses):
                if reqd_titles != '':
                    reqd_titles += ', '
                reqd_service = rc.lookupObject(reqd)
                reqd_titles += reqd_service.Title()
        if reqd_titles != '':
            this_analysis = dependant_services[analysis]
            error_key = this_analysis.Title()
            state.setError(error_key,
                    'needs %s' %(reqd_titles))

if state.getErrors():
    message=context.translate('message_correct_errors', default='Please correct the indicated errors', domain='bika')
    return state.set(
        status='failure',
        portal_status_message=message
    )
else:
    message=context.translate('message_spec_created', default='The analysis profile was successfully created', domain='bika')
    return state.set(
        portal_status_message=message)

