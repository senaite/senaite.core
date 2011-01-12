## Controller Python Script "analysisrequest_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Add analysis requests
##

from DateTime import DateTime

ARs = []

# strip the string containing the uid array into a list. 
# array context lost through javascript manipulation     
# must be a better way of doing this!
ccs = context.REQUEST.CCContact
ccs = ccs.replace('[',' ')
ccs = ccs.replace(']',' ')
ccs = ccs.replace("'"," ")
ccs = ccs.replace(',',' ')
ccs_list = ccs.split() 
saveProfiles = False

prices = context.REQUEST.form['Prices']
services = context.REQUEST.form['Services']

form_items = list(context.REQUEST.form.items())
form_items.sort()
for key, value in form_items:
    if not key.startswith('ar'):
        continue
    value = value.copy()
    ar_number = 1
    sample_state = 'due'
    if value.has_key('SampleID'):
        sample_id = value['SampleID']
        sample_uid = value['SampleUID']
        sample_proxy = context.portal_catalog(portal_type='Sample',
            getSampleID=sample_id) 
        assert len(sample_proxy) == 1
        sample = sample_proxy[0].getObject()
        ar_number = sample.getLastARNumber() + 1
        wf_tool = context.portal_workflow
        sample_state = wf_tool.getInfoFor(sample, 'review_state', '')
        sample.edit(LastARNumber=ar_number)
        sample.reindexObject()
    else:
        sample_id = context.generateUniqueId('Sample')
        context.invokeFactory(id=sample_id, type_name='Sample')
        sample = context[sample_id]
        sample.edit(
            SampleID=sample_id,
            LastARNumber=ar_number,
            DateSubmitted=DateTime(),
            SubmittedByUser=sample.current_user(),
            **dict(value)
            )
        if (value.has_key('DateSampledYear') and value.has_key('DateSampledMonth') and value.has_key('DateSampledDay')):
           dsy = value.get('DateSampledYear')
           dsm = value.get('DateSampledMonth')
           dsd = value.get('DateSampledDay')
           datesampled = dsy + "-" + dsm + "-" + dsd + " 00:00"
           sample.edit(DateSampled=datesampled)
        sample_uid = sample.UID()
        dis_date = sample.disposal_date()
        sample.setDisposalDate(dis_date)

    ar_id = context.generateARUniqueId('AnalysisRequest', sample_id, ar_number)
    context.invokeFactory(id=ar_id, type_name='AnalysisRequest')

    profile = None
    if (value.has_key('arprofiles')):
        profileUID = value['arprofiles']
        for proxy in context.portal_catalog(portal_type='ARProfile', UID = profileUID):
            profile = proxy.getObject()
        if profile == None:
           for proxy in context.portal_catalog(portal_type='LabARProfile', UID = profileUID):
               profile = proxy.getObject()

    ar = context[ar_id]
    ar.edit(
        RequestID=ar_id,
        DateRequested=DateTime(),
        Contact=context.REQUEST.Contact,
        CCContact=ccs_list,
        CCEmails=context.REQUEST.CCEmails,
        Sample=sample_uid,
        Profile=profile,
        **dict(value)
        )

    # decode analyses and prices
    analyses=[]
    for analysis in value['Analysis']:
        analyses.append('%s:%s' %(services[analysis], prices[analysis]))
    ar.setAnalyses(analyses)

    ARs.append(ar_id)

    if (value.has_key('profileTitle')):
        profile_id = context.generateUniqueId('ARProfile')
        context.invokeFactory(id=profile_id, type_name='ARProfile')
        profile = context[profile_id]
        ar.edit(Profile=profile)
        profile.setProfileTitle(value['profileTitle'])
        analyses = ar.getAnalyses() 
        services_array = [] 
        for a in analyses:
            services_array.append(a.getServiceUID())
        profile.setService(services_array)
        profile.reindexObject()

# AVS check sample_state and promote the AR is > 'due'

from Products.CMFPlone import transaction_note
print_ars = ', '.join(ARs)
transaction_note('%s created successfully' % print_ars)

message=context.translate('message_ar_created', default='Analysis requests ${ARs} were successfully created.', mapping={'ARs': print_ars}, domain='bika')
return state.set(portal_status_message=message)
