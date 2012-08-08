from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.client import ClientSamplesView
from bika.lims.utils import formatDateQuery, formatDateParms, \
                logged_in_client, TimeOrDate, pretty_user_name_or_id
from bika.lims.interfaces import IQueries
from plone.app.content.browser.interfaces import IFolderContentsView
from Products.CMFPlone.PloneBatch import Batch
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json
import plone

class QueryAnalysisRequests(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("query_out.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        # get all the data into datalines
        

        sc = getToolByName(self.context, 'bika_setup_catalog')
        bc = getToolByName(self.context, 'bika_catalog')
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        self.query_content = {}
        parm_lines = {}
        self.parms = []
        self.headings = {}
        self.headings['header'] = _("Analysis Requests")
        self.headings['subheader'] = _("Selected on the following criteria")

        count_all = 0
        query = {'portal_type': 'AnalysisRequest'}

        if self.request.form.has_key('ClientUID'):
            client_uid = self.request.form['ClientUID']
            query['getClientUID'] = client_uid
            client = rc.lookupObject(client_uid)
            client_title = client.Title()
        else:
            client = logged_in_client(self.context)
            if client:
                client_title = client.Title()
                query['getClientUID'] = client.UID()
            else:
                client_title = 'Undefined'
        self.parms.append(
            { 'title': _('Client'),
              'fieldid': 'ClientUID',
              'value': client_title,
              'type': 'text'})

        if self.request.form.has_key('ContactUID'):
            contact_uid = self.request.form['ContactUID']
            query['getContactUID'] = contact_uid
            contact = rc.lookupObject(contact_uid)
            contact_name = contact.getFullname()
        else:
            contact_name = 'Undefined'
        self.parms.append(
            { 'title': _('Contact'),
              'fieldid': 'ContactUID',
              'value': contact_name,
              'type': 'text'})

        if self.request.form.has_key('ProfileUID'):
            profile_uid = self.request.form['ProfileUID']
            query['getAnalysisProfileUID'] = profile_uid
            profile = rc.lookupObject(profile_uid)
            profile_title = profile.Title()
        else:
            profile_title = 'Undefined'
        self.parms.append(
            { 'title': _('Profile'),
             'value': profile_title,
             'type': 'text'})

        if self.request.form.has_key('RequestID'):
            request_id = self.request.form['RequestID']
            query['getRequestID'] = request_id
        else:
            request_id = 'Undefined'
        self.parms.append(
            { 'title': _('AR'),
             'value': request_id,
             'type': 'text'})

        if self.request.form.has_key('ClientOrderNumber'):
            clientoid = self.request.form['ClientOrderNumber']
            query['getClientOrderNumber'] = clientoid
        else:
            clientoid = 'Undefined'
        self.parms.append(
            { 'title': _('Client order number'),
             'value': clientoid,
             'type': 'text'})

        if self.request.form.has_key('ClientReference'):
            clientref = self.request.form['ClientReference']
            query['getClientReference'] = clientref
        else:
            clientref = 'Undefined'
        self.parms.append(
            { 'title': _('Client reference'),
             'value': clientref,
             'type': 'text'})

        if self.request.form.has_key('ClientSampleID'):
            clientsid = self.request.form['ClientSampleID']
            query['getClientSampleID'] = clientsid
        else:
            clientsid = 'Undefined'
        self.parms.append(
            { 'title': _('Client sample ID'),
             'value': clientsid,
             'type': 'text'})

        if self.request.form.has_key('SampleTypeUID'):
            st_uid = self.request.form['SampleTypeUID']
            query['getSampleTypeUID'] = st_uid
            st = rc.lookupObject(st_uid)
            st_title = st.Title()
        else:
            st_title = 'Undefined'
        self.parms.append(
            { 'title': _('Sample type'),
             'value': st_title,
             'type': 'text'})

        if self.request.form.has_key('SamplePointUID'):
            sp_uid = self.request.form['SamplePointUID']
            query['getSamplePointUID'] = sp_uid
            sp = rc.lookupObject(sp_uid)
            sp_title = sp.Title()
        else:
            sp_title = 'Undefined'
        self.parms.append(
            { 'title': _('Sample point'),
             'value': sp_title,
             'type': 'text'})

        date_query = formatDateQuery(self.context, 'DateSampled')
        if date_query:
            query['created'] = date_query
            sampled = formatDateParms(self.context, 'DateSampled') 
        else:
            sampled = 'Undefined'
        self.parms.append(
            { 'title': _('Sampled'),
             'value': sampled,
             'type': 'text'})

        date_query = formatDateQuery(self.context, 'DateRequested')
        if date_query:
            query['created'] = date_query
            requested = formatDateParms(self.context, 'DateRequested') 
        else:
            requested = 'Undefined'
        self.parms.append(
            { 'title': _('Requested'),
             'value': requested,
             'type': 'text'})

        date_query = formatDateQuery(self.context, 'DateReceived')
        if date_query:
            query['created'] = date_query
            received = formatDateParms(self.context, 'DateReceived') 
        else:
            received = 'Undefined'
        self.parms.append(
            { 'title': _('Received'),
             'value': received,
             'type': 'text'})

        date_query = formatDateQuery(self.context, 'DatePublished')
        if date_query:
            query['getDatePublished'] = date_query
            published = formatDateParms(self.context, 'DatePublished') 
        else:
            published = 'Undefined'
        self.parms.append(
            { 'title': _('Published'),
             'value': published,
             'type': 'text'})

        if self.request.form.has_key('CategoryUID'):
            category_uid = self.request.form['CategoryUID']
            query['getCategoryUID'] = category_uid
            category = rc.lookupObject(category_uid)
            category_title = category.Title()
        else:
            category_title = 'Undefined'
        self.parms.append(
            { 'title': _('Category'),
             'value': category_title,
             'type': 'text'})

        if self.request.form.has_key('ServiceUID'):
            service_uid = self.request.form['ServiceUID']
            query['getServiceUID'] = service_uid
            service = rc.lookupObject(service_uid)
            service_title = service.Title()
        else:
            service_title = 'Undefined'
        self.parms.append(
            { 'title': _('Analysis service'),
             'value': service_title,
             'type': 'text'})

        if self.request.form.has_key('Analyst'):
            analyst = self.request.form['Analyst']
            query['getAnalyst'] = analyst
            analyst_name = pretty_user_name_or_id(self.context, analyst)
        else:
            analyst_name = 'Undefined'
        self.parms.append(
            { 'title': _('Analyst'),
             'value': analyst_name,
             'type': 'text'})

        workflow = getToolByName(self.context, 'portal_workflow')
        if self.request.form.has_key('review_state'):
            query['review_state'] = self.request.form['review_state']
            review_state = workflow.getTitleForStateOnType(
                        self.request.form['review_state'], 'Analysis')
        else:
            review_state = 'Undefined'
        self.parms.append(
            { 'title': _('Status'),
             'value': review_state,
             'type': 'text'})

        if self.request.form.has_key('cancellation_state'):
            query['cancellation_state'] = self.request.form['cancellation_state']
            cancellation_state = workflow.getTitleForStateOnType(
                        self.request.form['cancellation_state'], 'Analysis')
        else:
            cancellation_state = 'Undefined'

        self.parms.append(
            { 'title': _('Active'),
             'value': cancellation_state,
             'type': 'text'})



        if self.request.form.has_key('ws_review_state'):
            query['worksheetanalysis_review_state'] = self.request.form['ws_review_state']
            ws_review_state = workflow.getTitleForStateOnType(
                        self.request.form['ws_review_state'], 'Analysis')
        else:
            ws_review_state = 'Undefined'

        self.parms.append(
            { 'title': _('Assigned to worksheet'),
             'value': ws_review_state,
             'type': 'text'})


        # and now lets do the actual query lines
        self.formats = {'columns': 7,
                   'col_heads': [], 
                   'class': '',
                  }

        self.columns = 6
        header_items = 17
        
        self.datalines = []
        clientoid_label =   [{'value': _("Client order ID"),
                              'class': 'header',}]
        clientref_label =   [{'value': _("Client reference"),
                              'class': 'header',}]
        clientsid_label =   [{'value': _("Client sample ID"),
                              'class': 'header',}]
        client_label =      [{'value': _("Client"),
                              'class': 'header',}]
        contact_label =     [{'value': _("Contact"),
                              'class': 'header',}]
        requestid_label =   [{'value': _("Request ID"),
                              'class': 'header',}]
        sampleid_label =    [{'value': _("Sample ID"),
                              'class': 'header',}]
        profile_label =     [{'value': _("Profile"),
                              'class': 'header',}]
        sampletype_label =  [{'value': _("Sample type"),
                              'class': 'header',}]
        samplepoint_label = [{'value': _("Sample point"),
                              'class': 'header',}]
        sampled_label =     [{'value': _("Sampled"),
                              'class': 'header',}]
        requested_label =   [{'value': _("Requested"),
                              'class': 'header',}]
        received_label =    [{'value': _("Received"),
                              'class': 'header',}]
        published_label =   [{'value': _("Published"),
                              'class': 'header',}]
        status_label =      [{'value': _("Status"),
                              'class': 'header',}]
        submittedby_label = [{'value': _("Submitted by"),
                              'class': 'header',}]
        verifiedby_label =  [{'value': _("Verified by"),
                              'class': 'header',}]
        i = 0
        clientoids = []
        clientrefs = []
        clientsids = []
        clients = []
        contacts = []
        requestids = []
        sampleids = []
        profiles = []
        sampletypes = []
        samplepoints = []
        sampleds = []
        requesteds = []
        receiveds = []
        publisheds = []
        statuses = []
        submittedbys = []
        verifiedbys = []

        def loadlines(detail_lines):
            for i in range(16):
                self.datalines.append(detail_lines[i])

        details = []
        for i in range(header_items):
            details.append([])

        ars = bc(query)
        self.url = self.request.URL
        self.show_all = False
        pagesize = 6
        # check for pagenumber 
        if self.request.form.has_key('b_start'):
            batch_start = self.request.form['b_start']
        else:
            batch_start = 1
        self.batch = Batch(ars, pagesize, batch_start)

        for arp in self.batch:
            ar = arp.getObject()
            details[0].append({'value': ar.getClientOrderNumber()})
            details[1].append({'value': ar.getClientReference()})
            details[2].append({'value': ar.getClientSampleID()})
            details[3].append({'value': ar.aq_parent.Title()})
            details[4].append({'value': ar.getContact().Title()})
            details[5].append({'value': ar.getRequestID()})
            details[6].append({'value': ar.getSample().getSampleID()})
            details[7].append({'value': ar.getProfile() and ar.getProfile().Title() or ' '})
            details[8].append({'value': ar.getSampleTypeTitle()})
            details[9].append({'value': ar.getSamplePointTitle()})
            details[10].append({'value': TimeOrDate(self.context, ar.getSample().getDateSampled())})
            details[11].append({'value': ' '})
            #details[11].append({'value': TimeOrDate(self.context, ar.created())})
            details[12].append({'value': TimeOrDate(self.context, ar.getDateReceived())})
            details[13].append({'value': TimeOrDate(self.context, ar.getDatePublished())})
            details[14].append({'value': ' '})
            #details[14].append({'value': ar.review_state()})
            details[15].append({'value': ' '})
            #details[15].append({'value': ar.getSubmittedBy().Title()})
            details[16].append({'value': ' '})
            #details[16].append({'value': ar.get_verifier().Title()})


            if len(details[0]) == self.columns:
                loadlines(details)
                details = []
                for i in range(header_items):
                    details.append([])

        for i in range(header_items):
            details.append([])

        if len(details[0]) > 0:
            loadlines(details)
        # footer data
        self.footlines = []
        footline = []
        footitem = {'value': _('Total'),
                    'class': 'total_label'} 
        footline.append(footitem)
        footitem = {'value': count_all} 
        footline.append(footitem)
        self.footlines.append(footline)
        
        return self.template()

    
