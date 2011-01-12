## Controller Python Script "validate_analysisrequest_add_form"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=validates analysis request add form
from DateTime import DateTime
from Products.bika.utils import sortable_title
portal = context.portal_url.getPortalObject()
current_year = DateTime().year()

def missing(field):
    message=context.translate('message_input_required', default='Input is required but no input given.', domain='bika')
    state.setError(field, message, 'ar_form_input_required')
if context.REQUEST.form.has_key('came_from'):
    came_from = context.REQUEST.form['came_from']
else:
    came_from = 'Add'
error_found = False
rc = context.reference_catalog
ar_analyses = {}
service_objs = {}
service_deps = {}

if context.REQUEST.form.has_key('Services'):
    prices = context.REQUEST.form['Prices']
    services = context.REQUEST.form['Services']
    categories = context.REQUEST.form['Categories']
else:
    error_key = 'All.Analyses'
    missing(error_key)
    prices = {}
    services = {}
    categories = {}


reqd_cats = []

required_fields = ('Analysis', 'SampleType' )
for key, value in context.REQUEST.form.items():
        
    if not key.startswith('ar'):
        continue

    # copy value so that we can manipulate it
    value = value.copy()

    # check for no analyses
    if not value.has_key('Analysis'):
        column_nr = int(key.split('.')[-1]) + 1
        error_key = '%s.%s' % (column_nr, 'Analysis')
        missing(error_key)

    # set total fields
    for k in ('Subtotal_submit', 'VAT_submit', 'Total_submit'):
        if not value.has_key(k):
            continue
        flat_key = '%s.%s' % (key, k)
        context.REQUEST.set(flat_key, value.get(k))
        del value[k]

    # delete the key so that we don't create an empty AR
    if not value:
        del context.REQUEST.form[key]
        continue

    analyses = []
    new_services = []
    numeric_analyses = []

    for k in ('Contact', 'CCEmails',  'ClientReference', 'ClientSampleID', 'SampleType', 'SamplePoint', 'ClientOrderNumber', 'Analysis', 'ReportDryMatter', 'InvoiceExclude', 'profileTitle', 'arprofiles', 'selectedservices', 'DateSampledYear', 'DateSampledMonth', 'DateSampledDay'):
        flat_key = '%s.%s' % (key, k)
        column_nr = int(key.split('.')[-1]) + 1
        error_key = '%s.%s' % (column_nr, k)
        if value.has_key(k):
            context.REQUEST.set(flat_key, value.get(k))
        else:
            if  k in required_fields:
                if k == 'SampleType' and came_from == 'Edit':
                    pass
                else:
                    missing(error_key)
                    error_found = True
        if k == 'SampleType' and value.has_key(k):
            rs = context.portal_catalog(
                portal_type='SampleType',
                sortable_title=sortable_title(portal, value[k])
            )
            if not rs:
                error_found = True
                state.setError(error_key,
                    '%s is not a valid sample type'%value[k])

        if k == 'Analysis' and value.has_key(k):
            numeric_analyses = value[k]
            analyses = []
            for analysis in numeric_analyses:
                analyses.append(services[analysis])
            for analysis in analyses:
                expand_cat = False
                reqd_services = []
                if service_objs.has_key(analysis):
                    this_service = service_objs[analysis]
                else:
                    this_service = rc.lookupObject(analysis)
                    service_objs[analysis] = this_service
                if this_service.getCalcType() == 'dep':
                    if service_deps.has_key(analysis):
                        reqd_services = service_deps[analysis]
                    else:
                        required = context.get_analysis_dependancies(this_service)
                        reqd_services = required['uids']
                        service_deps[analysis] = reqd_services

                reqd_titles = ''
                for reqd in reqd_services:
                    if reqd not in analyses:
                        if reqd not in new_services:
                            new_services.append(reqd)
                            if not service_objs.has_key(reqd):
                                that_service = rc.lookupObject(reqd)
                                service_objs[reqd] = that_service

                        that_service = service_objs[reqd]
                        if that_service.getCategoryUID() not in categories:
                            expand_cat = True
                            if that_service.getCategoryName() not in reqd_cats:
                                reqd_cats.append(that_service.getCategoryName())

                        if reqd_titles != '':
                            reqd_titles += ', '
                        reqd_titles += that_service.Title()

                if expand_cat:
                    error_key = '%s.%s' %(column_nr, this_service.Title())
                    state.setError(error_key,
                        '%s required - please expand categories indicated' %(reqd_titles))
                else:
                    if reqd_titles != '':
                        error_key = '%s.%s' %(column_nr, this_service.Title())
                        state.setError(error_key,
                            '%s required and added - please confirm' %(reqd_titles))
        # validate analysisrequest dependancies
        if k == 'ReportDryMatter' and value.has_key(k):
            if value[k] == 'on':
                expand_cat = False
                required = context.get_analysisrequest_dependancies('DryMatter')
                reqd_services = required['uids']
                reqd_titles = ''
                for reqd in reqd_services:
                    if reqd not in analyses:
                        if reqd not in new_services:
                            new_services.append(reqd)
                            if not service_objs.has_key(reqd):
                                that_service = rc.lookupObject(reqd)
                                service_objs[reqd] = that_service

                        that_service = service_objs[reqd]
                        if that_service.getCategoryUID() not in categories:
                            expand_cat = True
                            if that_service.getCategoryName() not in reqd_cats:
                                reqd_cats.append(that_service.getCategoryName())

                        if reqd_titles != '':
                            reqd_titles += ', '
                        reqd_titles += that_service.Title()

                if expand_cat:
                    error_key = '%s.%s' %(column_nr, 'Report as Dry Matter')
                    state.setError(error_key,
                        '%s required - please expand categories indicated' %(reqd_titles))
                else:
                    if reqd_titles != '':
                        error_key = '%s.%s' %(column_nr, 'Report as Dry Matter')
                        state.setError(error_key,
                            '%s required and added - please confirm' %(reqd_titles))

    if new_services:
        # switch the dictionary
        s_keys = services.keys()
        service_numbers = {}
        for s_key in s_keys:
            service_numbers[services[s_key]] = s_key

        reqd_subtotal = 0
        reqd_total = 0
        for service_uid in new_services:
            service = rc.lookupObject(service_uid)
            cat_uid = service.getCategoryUID()
            if service_numbers.has_key(service_uid): # cat is expanded
                service_number = service_numbers[service_uid]
                numeric_analyses.append(service_number)
                price = float(prices[service_number])          
                vatperc = service.getVAT()
                vat = price * vatperc / 100
                total = price + vat

                reqd_subtotal = reqd_subtotal + price
                reqd_total = reqd_total + total
                

        key_analyses = '%s.Analysis' %key
        context.REQUEST.set(key_analyses, numeric_analyses)

        sv_list = ''
        list_splitter = ''
        for sv in numeric_analyses:
            sv_list = sv_list + list_splitter + sv
            list_splitter = ','
        key_selectedservices = '%s.selectedservices' %key
        context.REQUEST.set(key_selectedservices, sv_list)

        key_arprofiles = '%s.arprofiles' %key
        context.REQUEST.set(key_arprofiles, '')

        reqd_vat = reqd_total - reqd_subtotal
        subtotal_key = '%s.Subtotal_submit' %(key)
        old_subtotal = context.REQUEST.get(subtotal_key, 0.0)
        new_subtotal = float(old_subtotal) + reqd_subtotal
        context.REQUEST.set(subtotal_key, '%.2f' %new_subtotal)
        vat_key = '%s.VAT_submit' %(key)
        old_vat = context.REQUEST.get(vat_key, 0.0)
        new_vat = float(old_vat) + reqd_vat
        context.REQUEST.set(vat_key, '%.2f' %new_vat)
        total_key = '%s.Total_submit' %(key)
        old_total = context.REQUEST.get(total_key, 0.0)
        new_total = float(old_total) + reqd_total
        context.REQUEST.set(total_key, '%.2f' %new_total)

cat_names = ''
for reqd in reqd_cats:
    if cat_names:
        cat_names += ', '
    cat_names += reqd

if cat_names:
    error_key = 'All.Analyses' 
    state.setError(error_key,
        'Expand categories for required analyses: %s' %(cat_names))
    
if state.getErrors():
    # set the prices to flat key for form reinput
    for key in prices.keys():
        num_key = int(key)
        context.REQUEST.set('Prices.%s' %num_key, float(prices[key]))
    if error_found:
        message=context.translate('message_correct_errors', default='Please correct the indicated errors', domain='bika')
    else:
        message=context.translate('message_confirm_changes', default='Please confirm changes', domain='bika')

if state.getErrors():
    return state.set(
        status='failure',
        portal_status_message=message
    )
else:
    message=context.translate('message_ar_created', default='The analysis requests were successfully created', domain='bika')
    return state.set(
        portal_status_message=message)

