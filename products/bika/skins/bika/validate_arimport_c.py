## Script (Python) "validate_arimport"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=arimport
##title=validates arimport and always saves
## validates the arimport batch, and writes error messages to Remarks column

rc = context.reference_catalog
client = arimport.aq_parent
batch_remarks = []
valid_batch = True
order_id = arimport.getOrderID()
uid = arimport.UID()
batches = context.portal_catalog(portal_type='ARImport', 
            getClientUID = client.UID(),
            getOrderID=order_id)
for batch in batches:
    if batch.UID == uid:
        continue
    oldbatch = batch.getObject()
    if oldbatch.getStatus():
        # then a previous valid batch exists
        batch_remarks.append('\n' + 'Duplicate order')

# validate client
if arimport.getClientID() != client.getClientID():
    batch_remarks.append('\n' + 'Client ID should be %s' %client.getClientID())
    valid_batch = False

# validate contact
contact_found = False 
cc_contact_found = False 

if arimport.getContact():
    contact_found = True
else:
    contact_uname = arimport.getContactID()
    for contact in client.objectValues('Contact'):
        if contact.getUsername() == contact_uname:
            arimport.edit(Contact=contact)
            contact_found = True
            break

if arimport.getCCContact():
    cc_contact_found = True
else:
    if arimport.getCCContactID():
        cccontact_uname = arimport.getCCContactID()
        for contact in client.objectValues('Contact'):
            if contact.getUsername() == cccontact_uname:
                arimport.edit(CCContact=contact)
                cc_contact_found = True
                break

cccontact_uname = arimport.getCCContactID()

if not contact_found:
    batch_remarks.append('\n' + 'Contact invalid')
    valid_batch = False
if cccontact_uname != None and \
   cccontact_uname != '':
    if not cc_contact_found:
        batch_remarks.append('\n' + 'CC contact invalid')
        valid_batch = False

# validate sample point
samplepoint = arimport.getSamplePoint()
if samplepoint != None:
    r = context.portal_catalog(portal_type='SamplePoint', 
        Title=samplepoint)
    if len(r) == 0:
        batch_remarks.append('\n' + 'New Sample point will be added')

sampletypes = [p.Title for p in context.portal_catalog(portal_type="SampleType")]
service_keys = []
dependant_services = {}
for s in context.portal_catalog(portal_type="AnalysisService"):
    service = s.getObject()
    service_keys.append(service.getAnalysisKey())
    if service.getCalcType() == 'dep':
        dependant_services[service.getAnalysisKey()] = service

aritems = arimport.objectValues('ARImportItem')
for aritem in aritems:
    item_remarks = []
    valid_item = True
    if aritem.getSampleType() not in sampletypes:
        batch_remarks.append('\n' + '%s: Sample type %s invalid' %(aritem.getSampleName(), aritem.getSampleType()))
        item_remarks.append('\n' + 'Sample type %s invalid' %(aritem.getSampleType()))
        valid_item = False
    #validate Sample Date
    try:
        date_items = aritem.getSampleDate().split('/')
        test_date = DateTime(int(date_items[2]), int(date_items[1]), int(date_items[0]))
    except:
        valid_item = False
        batch_remarks.append('\n' + '%s: Sample date %s invalid' %(aritem.getSampleName(), aritem.getSampleDate()))
        item_remarks.append('\n' + 'Sample date %s invalid' %(aritem.getSampleDate()))

    analyses = aritem.getAnalyses()
    for analysis in analyses:
        if analysis not in service_keys:
            batch_remarks.append('\n' + '%s: Analysis %s invalid' %(aritem.getSampleName(), analysis))
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
                %(aritem.getSampleName(), analysis, reqd_titles))
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
                %(aritem.getSampleName(), reqd_titles))
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
