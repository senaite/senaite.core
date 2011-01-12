## Script (Python) "validate_arimport_s"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=arimport
##title=validates arimport and always saves - special import option
## validates the arimport batch, and writes error messages to Remarks column

client = arimport.aq_parent
batch_remarks = []
valid_batch = True
uid = arimport.UID()

# validate client
if arimport.getClientName() != client.Title():
    batch_remarks.append('\n' + 'Client Name should be %s' %client.Title())
    valid_batch = False

# validate contact
contact_found = False 

if arimport.getContact():
    contact_found = True
else:
    contact_name = arimport.getContactName()
    for contact in client.objectValues('Contact'):
        if contact.Title() == contact_name:
            arimport.edit(Contact=contact)
            contact_found = True
            break

if not contact_found:
    batch_remarks.append('\n' + 'Contact invalid')
    valid_batch = False

sampletypes = [p.Title for p in context.portal_catalog(portal_type="SampleType")]
service_keys = []
dependant_services = {}
for s in context.portal_catalog(portal_type="AnalysisService"):
    service = s.getObject()
    service_keys.append(service.getAnalysisKey())
    if service.getCalcType() == 'dep':
        dependant_services[service.getAnalysisKey()] = service

profile_keys = []
for p in context.portal_catalog(portal_type="LabARProfile"):
    profile = p.getObject()
    profile_keys.append(profile.getProfileKey())
for p in context.portal_catalog(portal_type="ARProfile",
                                getClientUID=client.UID()):
    profile = p.getObject()
    profile_keys.append(profile.getProfileKey())

aritems = arimport.objectValues('ARImportItem')
for aritem in aritems:
    item_remarks = []
    valid_item = True
    if aritem.getSampleType() not in sampletypes:
        batch_remarks.append('\n' + '%s: Sample type %s invalid' %(aritem.getClientRef(), aritem.getSampleType()))
        item_remarks.append('\n' + 'Sample type %s invalid' %(aritem.getSampleType()))
        valid_item = False
    #validate Sample Date
    if aritem.getSampleDate():
        try:
            date_items = aritem.getSampleDate().split('/')
            test_date = DateTime(int(date_items[2]), int(date_items[0]), int(date_items[1]))
            year = int(date_items[2])
            if year < 99:
                year += 2000
            if year < 1900:
                valid_item = False
                batch_remarks.append('\n' + '%s: Sample date %s should be after 1900' %(aritem.getClientRef(), aritem.getSampleDate()))
                item_remarks.append('\n' + 'Sample date %s should be after 1900' %(aritem.getSampleDate()))
        except:
            valid_item = False
            batch_remarks.append('\n' + '%s: Sample date %s invalid' %(aritem.getClientRef(), aritem.getSampleDate()))
            item_remarks.append('\n' + 'Sample date %s invalid' %(aritem.getSampleDate()))

    # validate profiles
    profiles = aritem.getAnalysisProfile()
    for profile in profiles:
        if profile not in profile_keys:
            batch_remarks.append('\n' + '%s: Profile %s invalid' %(aritem.getClientRef(), profile))
            item_remarks.append('\n' + 'Profile %s invalid' %(profile))
            valid_item = False

    # validate analyses
    analyses = aritem.getAnalyses()
    for analysis in analyses:
        if analysis not in service_keys:
            batch_remarks.append('\n' + '%s: Analysis %s invalid' %(aritem.getClientRef(), analysis))
            item_remarks.append('\n' + 'Analysis %s invalid' %(analysis))
            valid_item = False
        # validate analysis dependancies
        reqd_analyses = []
        if dependant_services.has_key(analysis):
            this_analysis = dependant_services[analysis]
            required = context.get_analysis_dependancies(this_analysis)
            reqd_analyses = required['keys']
        reqd_titles = ''
        for reqd in reqd_analyses:
            if (reqd not in analyses):
                if reqd_titles != '':
                    reqd_titles += ', '
                reqd_titles += reqd
        if reqd_titles != '':
            valid_item = False
            batch_remarks.append('\n' + '%s: %s needs %s' \
                %(aritem.getClientRef(), analysis, reqd_titles))
            item_remarks.append('\n' + '%s needs %s' \
                %(analysis, reqd_titles))

    # validate analysisrequest dependancies
    if aritem.getReportDryMatter().lower() == 'y':
        required = context.get_analysisrequest_dependancies('DryMatter')
        reqd_analyses = required['keys']
        reqd_titles = ''
        for reqd in reqd_analyses:
            if reqd not in analyses:
                if reqd_titles != '':
                    reqd_titles += ', '
                reqd_titles += reqd

        if reqd_titles != '':
            valid_item = False
            batch_remarks.append('\n' + '%s: Report as Dry Matter needs %s' \
                %(aritem.getClientRef(), reqd_titles))
            item_remarks.append('\n' + 'Report as Dry Matter needs %s' \
                %(reqd_titles))

    aritem.edit(
        Remarks=item_remarks)
    if not valid_item:
        valid_batch = False
arimport.edit(
    Remarks=batch_remarks,
    Status=valid_batch)

return valid_batch
