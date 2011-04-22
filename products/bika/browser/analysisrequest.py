from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import datetime
from DateTime import DateTime
import json

def analysisrequest_add_submit(context, request):

    form = request.form
    portal = getToolByName(context, 'portal_url').getPortalObject()
    rc = getToolByName(context, 'reference_catalog')
    pc = getToolByName(context, 'portal_catalog')

    errors = {}
    def error(field=None, column=None,message = None):
        if not message:
            message = context.translate('message_input_required',
                                        default = 'Input is required but no input given.', 
                                        domain = 'bika')
        colstr = column != None and "%s."%column or ""
        fieldstr = field != None and field or ""
        error_key = "%s%s" % (colstr, field) or 'Form error'
        try: errors[error_key].append(message)
        except: errors[error_key] = [message, ]

    came_from = form.has_key('came_from') and form['came_from'] or 'Add'

    import pprint
    pprint.pprint(request.form)

    # first some basic validation

    required = ('Analyses', 'SampleType', 'DateSampled')
    fields = ('SampleID', 'ClientOrderNumber', 'ClientReference', 
              'ClientSampleID', 'DateSampled', 'SampleType', 'SamplePoint', 
              'ReportDryMatter', 'InvoiceExclude', 'Analyses')
   
    try:
        prices = form['Prices']
        vat = form['VAT']
    except KeyError:
        return error(message="No analyses selected.")

    for column in range(int(form['col_count'])):
        if not form.has_key("ar.%s" % column):
            continue
        ar = form["ar.%s" % column]
        if len(ar.keys()) == 3:
            continue

        # check that required fields have values
        for field in required:
            if not ar.has_key(field):
                error(column, field)

        # validate all field values
        for field in fields:
            # ignore empty field values
            if not ar.has_key(field):
                continue

            if field == "SampleID":
                if not pc(portal_type = 'Sample',
                          getSampleID = ar[field]):
                    error(column, field, '%s is not a valid sample ID' % ar[field])

            elif field == "SampleType":
                if not pc(portal_type = 'SampleType',
                          Title = ar[field]):
                    error(column, field, '%s is not a valid sample type' % ar[field])

            elif field == "SamplePoint":
                if not pc(portal_type = 'SamplePoint',
                          Title = ar[field]):
                    error(column, field, '%s is not a valid sample point' % ar[field])

            #elif field == "ReportDryMatter":
            #elif field == "InvoiceExclude":
            # elif field == "DateSampled":
            # XXX Should we check that these three are unique? :
            #elif field == "ClientOrderNumber":
            #elif field == "ClientReference":
            #elif field == "ClientSampleID":

    if errors:
        print "errors: ", errors
        return json.dumps(errors)

    ARs = []
    services = {} # UID:service

    # The actual submission

    for column in range(int(form['col_count'])):
        if not form.has_key("ar.%s" % column):
            continue
        values = form["ar.%s" % column].copy()
        if len(values.keys()) == 3:
            continue

        ar_number = 1
        sample_state = 'due'

        profile = None
        if (values.has_key('ARProfile')):
            profileUID = values['ARProfile']
            for proxy in pc(portal_type = 'ARProfile',
                            UID = profileUID):
                profile = proxy.getObject()
            if profile == None:
                for proxy in pc(portal_type = 'LabARProfile',
                                UID = profileUID):
                    profile = proxy.getObject()

        if values.has_key('SampleID'):
            # Secondary AR
            sample_id = values['SampleID']
            sample_uid = values['SampleUID']
            sample_proxy = pc(portal_type = 'Sample',
                              getSampleID = sample_id)
            assert len(sample_proxy) == 1
            sample = sample_proxy[0].getObject()
            ar_number = sample.getLastARNumber() + 1
            wf_tool = context.portal_workflow
            sample_state = wf_tool.getInfoFor(sample,
                                              'review_state', '')
            sample.edit(LastARNumber = ar_number)
            sample.reindexObject()
        else:
            # Primary AR
            sample_id = context.generateUniqueId('Sample')
            context.invokeFactory(id = sample_id, type_name = 'Sample')
            sample = context[sample_id]
            sample.edit(
                SampleID = sample_id,
                LastARNumber = ar_number,
                DateSubmitted = DateTime(),
                SubmittedByUser = sample.current_user(),
                **dict(values)
            )
            sample_uid = sample.UID()
            dis_date = sample.disposal_date()
            sample.setDisposalDate(dis_date)

        # create AR

        Analyses = values['Analyses']
        del values['Analyses']

        ar_id = context.generateARUniqueId('AnalysisRequest', sample_id, ar_number)
        context.invokeFactory(id = ar_id, type_name = 'AnalysisRequest')
        ar = context[ar_id]
        ar.edit(
            RequestID = ar_id,
            DateRequested = DateTime(),
            Contact = form['Contact'],
            CCContact = form['cc_uids'].split(","),
            CCEmails = form['CCEmails'],
            Sample = sample_uid,
            Analyses = [ '%s:%s'%(a,prices[a]) for a in Analyses ] ,
            Profile = profile,
            **dict(values)
            )

        # create Analysis objects
        # ar.setAnalyses(Analyses)

        if (values.has_key('profileTitle')):
            profile_id = context.generateUniqueId('ARProfile')
            context.invokeFactory(id = profile_id, type_name = 'ARProfile')
            profile = context[profile_id]
            ar.edit(Profile = profile)
            profile.setProfileTitle(values['profileTitle'])
            analyses = ar.getAnalyses()
            services_array = []
            for a in analyses:
                services_array.append(a.getServiceUID())
            profile.setService(services_array)
            profile.reindexObject()

        ARs.append(ar_id)

    # AVS check sample_state and promote the AR is > 'due'

    return "Successfully created new AR%s" % (len(ARs) > 1 and 's' or '')

class AnalysisRequestAddView(BrowserView):
    """ The main AR Add form
    """
    template = ViewPageTemplateFile("templates/analysisrequest_add.pt")

    col_count = 4

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        request.set('disable_border', 1)

    def __call__(self):
        import pprint
        if self.request.form.has_key("submitted"):
            analysisrequest_add_submit(self.context, self.request)
        else:
            return self.template()

    def portal(self):
        portal_url = getToolByName(self, 'portal_url')
        return portal_url.absolute_url()

    def arprofiles(self):
        """ Return applicable client and Lab ARProfile records
        """
        profiles = []
        pc = getToolByName(self.context, 'portal_catalog')
        for proxy in pc(portal_type = 'ARProfile', getClientUID = self.context.UID(), sort_on = 'sortable_title'):
            profiles.append(proxy.getObject()) #XXX getObject()
        for proxy in pc(portal_type = 'LabARProfile', sort_on = 'sortable_title'):
            profile = proxy.getObject()
            profile.setTitle("Lab: %s" % profile.Title())
            profiles.append(proxy.getObject()) #XXX getObject()
        return profiles

    def Categories(self):
        """ Dictionary keys: field/lab
            Dictionary values: (Category Title,category UID)
        """
        pc = getToolByName(self.context, 'portal_catalog')
        cats = {}
        for service in pc(portal_type = "AnalysisService"):
            poc = service.getPointOfCapture
            if not cats.has_key(poc): cats[poc] = []
            cat = (service.getCategoryName, service.getCategoryUID)
            if cat not in cats[poc]: cats[poc].append(cat)
        return cats

class AnalysisRequestContactCCs(BrowserView):
    """ Returns lists of UID/Title for preconfigured CC contacts 
        When a client contact is selected from the #contact dropdown,
        the dropdown's ccuids attribute is set to the Contact UIDS 
        returned here, and the #cc_titles textbox is filled with Contact Titles
    """
    def __call__(self):
        rc = getToolByName(self.context, 'reference_catalog')
        uid = self.request.form.keys()[0]
        contact = rc.lookupObject(uid)
        cc_uids = []
        cc_titles = []
        for cc in contact.getCCContact():
            cc_uids.append(cc.UID())
            cc_titles.append(cc.Title())
        return json.dumps([",".join(cc_uids), ",".join(cc_titles)])

class AnalysisRequestSelectCCView(BrowserView):
    """ The CC Selector popup window uses this view
    """
    template = ViewPageTemplateFile("templates/analysisrequest_select_cc.pt")
    def __call__(self):
        return self.template()


class AnalysisRequestSelectSampleView(BrowserView):
    """ The Sample Selector popup window uses this view
    """
    template = ViewPageTemplateFile("templates/analysisrequest_select_sample.pt")
    def Samples(self, client):
        pc = getToolByName(self.context, 'portal_catalog')
        return pc(portal_type = "Sample", getClient = client)

    def __call__(self):
        return self.template()

class AnalysisRequest_AnalysisServices(BrowserView):
    """ AJAX requests pull this data for insertion when category header rows are clicked.
        The view returns a standard pagetemplate, the entire html of which is inserted.
    """
    template = ViewPageTemplateFile("templates/analysisrequest_analysisservices.pt")
    def __call__(self):
        return self.template()

    def Services(self, CategoryUID, poc):
        """ return a list of brains
        """
        pc = getToolByName(self, 'portal_catalog')
        return pc(portal_type = "AnalysisService", getCategoryUID = CategoryUID, getPointOfCapture = poc)

    def CalcDependancy(self, column, serviceUID):
        """ return {'categoryIDs': [element IDs of category TRs], 
                    'serviceUIDs': [dependant service UIDs]}
        """
        pc = getToolByName(self, 'portal_catalog')
        rc = getToolByName(self, 'reference_catalog')
        service = rc.lookupObject(serviceUID)
        depcatIDs = []
        depUIDs = []
        for depUID in service.getCalcDependancyUIDS():
            dep_service = rc.lookupObject(depUID)
            depcat_id = dep_service.getCategoryUID() + "_" + dep_service.PointOfCapture
            if depcat_id not in depcatIDs: depcatIDs.append(depcat_id)
            depUIDs.append(depUID)
        return {'categoryIDs':depcatIDs, 'serviceUIDs':depUIDs}

class AnalysisRequest_ProfileServices(BrowserView):
    """ AJAX requests pull this to retrieve a list of services in an AR Profile.
        return JSON data {categoryUID: [serviceUID,serviceUID], ...}
    """
    def __call__(self):
        rc = getToolByName(self, 'reference_catalog')
        pc = getToolByName(self, 'portal_catalog')
        profile = rc.lookupObject(self.request['profileUID'])
        if not profile: return

        services = {}
        for service in profile.getService():
            service = pc(portal_type = "AnalysisService", UID = service.UID())[0]
            categoryUID = service.getCategoryUID
            poc = service.getPointOfCapture
            try: services["%s_%s" % (categoryUID, poc)].append(service.UID)
            except: services["%s_%s" % (categoryUID, poc)] = [service.UID, ]
        return json.dumps(services)

class AnalysisRequest_SampleTypes(BrowserView):
    """ autocomplete data source for sample types field
        return JSON data [string,string]
    """
    def __call__(self):
        pc = getToolByName(self, 'portal_catalog')
        term = self.request.get('term', '')
        items = [s.Title for s in pc(portal_type = "SampleType") if s.Title.find(term) > -1]
        return json.dumps(items)

class AnalysisRequest_SamplePoints(BrowserView):
    """ autocomplete data source for sample points field
        return JSON data [string,string]
    """
    def __call__(self):
        pc = getToolByName(self, 'portal_catalog')
        term = self.request.get('term', '')
        items = [s.Title for s in pc(portal_type = "SamplePoint") if s.Title.find(term) > -1]
        return json.dumps(items)


