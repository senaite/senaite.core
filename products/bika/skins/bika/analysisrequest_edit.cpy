## Controller Python Script "analysisrequest_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Edit analysis request
##

from DateTime import DateTime

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

uid = context.REQUEST.form['AnalysisRequestUID']
rc = context.reference_catalog
ar = rc.lookupObject(uid)
form_items = list(context.REQUEST.form.items())
form_items.sort()
for key, value in form_items:
    if not key.startswith('ar'):
        continue
    value = value.copy()

    profile = None
    if (value.has_key('arprofiles')):
        profileUID = value['arprofiles']
        for proxy in context.portal_catalog(portal_type='ARProfile', UID = profileUID):
            profile = proxy.getObject()
        if profile == None:
           for proxy in context.portal_catalog(portal_type='LabARProfile', UID = profileUID):
               profile = proxy.getObject()

    ar.edit(
        Contact=context.REQUEST.Contact,
        CCContact=ccs_list,
        CCEmails=context.REQUEST.CCEmails,
        Notes=context.REQUEST.Notes,
        Profile=profile,
        **dict(value)
        )

    # decode analyses and prices
    analyses=[]
    for analysis in value['Analysis']:
        analyses.append('%s:%s' %(services[analysis], prices[analysis]))
    ar.setAnalyses(analyses)

    drymatter = False
    if value.has_key('ReportDryMatter'):
        drymatter = value['ReportDryMatter']
        if drymatter == 'on':
            drymatter = True
    exclude = False
    if value.has_key('InvoiceExclude'):
        exclude = value['InvoiceExclude']
        if exclude == 'on':
            exclude = True
    ar.edit(
        ReportDryMatter=drymatter,
        InvoiceExclude=exclude
        )

    if (value.has_key('profileTitle')):
        profile_id = context.generateUniqueId('ARProfile')
        client = context.aq_parent
        client.invokeFactory(id=profile_id, type_name='ARProfile')
        profile = client[profile_id]
        ar.edit(Profile=profile)
        profile.setProfileTitle(value['profileTitle'])
        analyses = ar.getAnalyses() 
        services_array = [] 
        for a in analyses:
            services_array.append(a.getServiceUID())
        profile.setService(services_array)
        profile.reindexObject()

from Products.CMFPlone import transaction_note
transaction_note('%s modified successfully' % ar.getRequestID())

message=context.translate('message_ar_modified', default='Analysis request ${AR} successfully modified.', mapping={'AR': ar.getRequestID()}, domain='bika')
return state.set(portal_status_message=message)
