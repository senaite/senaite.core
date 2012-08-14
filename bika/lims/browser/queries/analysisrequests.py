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
        self.datalines = []
        workflow = getToolByName(self, 'portal_workflow')

        # check for batch size
        if self.request.form.has_key('size'):
            batch_size = self.request.form['size']
        else:
            batch_size = 6

        # check for batch start
        if self.request.form.has_key('b_start'):
            batch_start = self.request.form['b_start']
        else:
            batch_start = 0

        sc = getToolByName(self.context, 'bika_setup_catalog')
        bc = getToolByName(self.context, 'bika_catalog')
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        self.query_content = {}
        parm_lines = {}
        self.parms = []
        self.headings = {}
        self.headings['header'] = _("Analysis Requests")
        self.headings['head_parms'] = _("Selected on the following criteria")
        self.headings['head_undefined'] = _("Parameters undefined")

        count_all = 0
        query = {'portal_type': 'AnalysisRequest'}

        undefined = []

        # Client
        client_title = None
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
        if client_title:
            self.parms.append(
                { 'title': _('Client'),
                  'fieldid': 'ClientUID',
                  'value': client_title,
                  'type': 'text'})
        else:
            undefined.append('Client')

        # Contact
        if self.request.form.has_key('ContactUID'):
            contact_uid = self.request.form['ContactUID']
            query['getContactUID'] = contact_uid
            contact = rc.lookupObject(contact_uid)
            contact_name = contact.getFullname()
            self.parms.append(
                { 'title': _('Contact'),
                  'fieldid': 'ContactUID',
                  'value': contact_name,
                  'type': 'text'})
        else:
            undefined.append('Contact')

        # Profile
        if self.request.form.has_key('ProfileUID'):
            profile_uid = self.request.form['ProfileUID']
            query['getAnalysisProfileUID'] = profile_uid
            profile = rc.lookupObject(profile_uid)
            profile_title = profile.Title()
            self.parms.append(
                { 'title': _('Profile'),
                 'value': profile_title,
                 'type': 'text'})
        else:
            undefined.append('Profile')

        # Request ID
        if self.request.form.has_key('RequestID'):
            request_id = self.request.form['RequestID']
            query['getRequestID'] = request_id
            self.parms.append(
                { 'title': _('AR'),
                 'value': request_id,
                 'type': 'text'})
        else:
            undefined.append('AR')

        # Client order number
        if self.request.form.has_key('ClientOrderNumber'):
            clientoid = self.request.form['ClientOrderNumber']
            query['getClientOrderNumber'] = clientoid
            self.parms.append(
                { 'title': _('Client order number'),
                 'value': clientoid,
                 'type': 'text'})
        else:
            undefined.append('Client order number')

        # Client reference
        if self.request.form.has_key('ClientReference'):
            clientref = self.request.form['ClientReference']
            query['getClientReference'] = clientref
            self.parms.append(
                { 'title': _('Client reference'),
                 'value': clientref,
                 'type': 'text'})
        else:
            undefined.append('Client reference')

        # Client sample ID
        if self.request.form.has_key('ClientSampleID'):
            clientsid = self.request.form['ClientSampleID']
            query['getClientSampleID'] = clientsid
            self.parms.append(
                { 'title': _('Client sample ID'),
                 'value': clientsid,
                 'type': 'text'})
        else:
            undefined.append('Client sample ID')

        # Sample type
        if self.request.form.has_key('SampleTypeUID'):
            st_uid = self.request.form['SampleTypeUID']
            query['getSampleTypeUID'] = st_uid
            st = rc.lookupObject(st_uid)
            st_title = st.Title()
            self.parms.append(
                { 'title': _('Sample type'),
                  'value': st_title,
                  'type': 'text'})
        else:
            undefined.append('Sample type')

        # Sample point
        if self.request.form.has_key('SamplePointUID'):
            sp_uid = self.request.form['SamplePointUID']
            query['getSamplePointUID'] = sp_uid
            sp = rc.lookupObject(sp_uid)
            sp_title = sp.Title()
            self.parms.append(
               { 'title': _('Sample point'),
                 'value': sp_title,
                 'type': 'text'})
        else:
            undefined.append('Sample point')

        # Date sampled
        date_query = formatDateQuery(self.context, 'DateSampled')
        if date_query:
            query['created'] = date_query
            sampled = formatDateParms(self.context, 'DateSampled')
            self.parms.append(
                { 'title': _('Sampled'),
                 'value': sampled,
                 'type': 'text'})
        else:
            undefined.append('Sampled')

        # Date requested
        date_query = formatDateQuery(self.context, 'DateRequested')
        if date_query:
            query['created'] = date_query
            requested = formatDateParms(self.context, 'DateRequested')
            self.parms.append(
                { 'title': _('Requested'),
                 'value': requested,
                 'type': 'text'})
        else:
            undefined.append('Requested')

        # Date received
        date_query = formatDateQuery(self.context, 'DateReceived')
        if date_query:
            query['created'] = date_query
            received = formatDateParms(self.context, 'DateReceived')
            self.parms.append(
                { 'title': _('Received'),
                 'value': received,
                 'type': 'text'})
        else:
            undefined.append('Received')

        # Date published
        date_query = formatDateQuery(self.context, 'DatePublished')
        if date_query:
            query['getDatePublished'] = date_query
            published = formatDateParms(self.context, 'DatePublished')
            self.parms.append(
                { 'title': _('Published'),
                 'value': published,
                 'type': 'text'})
        else:
            undefined.append('Published')

        # Category
        if self.request.form.has_key('CategoryUID'):
            category_uid = self.request.form['CategoryUID']
            query['getCategoryUID'] = category_uid
            category = rc.lookupObject(category_uid)
            category_title = category.Title()
            self.parms.append(
                { 'title': _('Category'),
                 'value': category_title,
                 'type': 'text'})
        else:
            undefined.append('Category')

        # Analysis service
        if self.request.form.has_key('ServiceUID'):
            service_uid = self.request.form['ServiceUID']
            query['getServiceUID'] = service_uid
            service = rc.lookupObject(service_uid)
            service_title = service.Title()
            self.parms.append(
                {'title': _('Analysis service'),
                 'value': service_title,
                 'type': 'text'})
        else:
            undefined.append('Analysis service')

        # Analyst
        if self.request.form.has_key('Analyst'):
            analyst = self.request.form['Analyst']
            query['getAnalyst'] = analyst
            analyst_name = pretty_user_name_or_id(self.context, analyst)
            self.parms.append(
                {'title': _('Analyst'),
                 'value': analyst_name,
                 'type': 'text'})
        else:
            undefined.append('Analyst')

        # Status
        if self.request.form.has_key('review_state'):
            query['review_state'] = self.request.form['review_state']
            review_state = workflow.getTitleForStateOnType(
                        self.request.form['review_state'], 'Analysis')
            self.parms.append(
                {'title': _('Status'),
                 'value': review_state,
                 'type': 'text'})
        else:
            undefined.append('Status')

        # Cancellation state
        if self.request.form.has_key('cancellation_state'):
            query['cancellation_state'] = self.request.form['cancellation_state']
            cancellation_state = workflow.getTitleForStateOnType(
                        self.request.form['cancellation_state'], 'Analysis')
            self.parms.append(
                {'title': _('Active'),
                 'value': cancellation_state,
                 'type': 'text'})
        else:
            undefined.append('Active')



        # Assigned to worksheet
        if self.request.form.has_key('ws_review_state'):
            query['worksheetanalysis_review_state'] = self.request.form['ws_review_state']
            ws_review_state = workflow.getTitleForStateOnType(
                        self.request.form['ws_review_state'], 'Analysis')
            self.parms.append(
                {'title': _('Assigned to worksheet'),
                 'value': ws_review_state,
                 'type': 'text'})
        else:
            undefined.append('Assigned to worksheet')


        # set up the undefined parameters in pretty format
        undefined_string = ', '.join(undefined)
        self.parms_undefined = [{'title': _('Parameters not defined'),
                                 'value': undefined_string}]

        self.columns = batch_size + 1
        # and now lets do the actual query lines
        self.formats = {'columns': self.columns,
                   'col_heads': [],
                   'class': '',
                  }


        labels = ["Client order ID",
                  "Client reference",
                  "Client sample ID",
                  "Client",
                  "Contact",
                  "Request ID",
                  "Sample ID",
                  "Profile",
                  "Sample type",
                  "Sample point",
                  "Sampled",
                  "Requested",
                  "Received",
                  "Published",
                  "Status",
                  "Submitted by",
                  "Verified by"]
        for label in labels:
            self.datalines.append([{'value': _(label),
                                    'class': 'header',}])

        details = []
        for i in range(len(self.datalines)):
            details.append([])

        ars = bc(query)
        self.url = self.request.URL
        self.show_all = False

        self.batch = Batch(ars, batch_size, batch_start)

        analyses = []
        ar_ids = []
        analysis_dict = {}
        service_dict = {}
        for arp in self.batch:
            ar = arp.getObject()
            ar_ids.append(ar.getRequestID())
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
            details[11].append({'value': TimeOrDate(self.context, ar.created())})
            details[12].append({'value': TimeOrDate(self.context, ar.getDateReceived())})
            details[13].append({'value': TimeOrDate(self.context, ar.getDatePublished())})
            details[14].append({'value': workflow.getInfoFor(ar, 'review_state')})
            #details[15].append({'value': ar.getSubmittedBy().Title()})
            details[15].append({'value': ' '})

            details[16].append({'value': ar.get_verifier().Title()})

            #analyses
            for analysis in ar.getAnalyses():
                service_uid = analysis.getServiceUID()
                if not service_dict.has_key(analysis.Title()):
                    service_dict['analysis.Title()'] = service_uid
                if not analysis_dict.has_key(service_uid):
                    analysis_dict[service_uid] = {}
                ar_index = ar_ids.index(ar.getRequestID())
                analysis_dict[service_uid] = {ar_index: analysis.getResult()}

            if len(details[0]) == batch_size:
                break


        # load the detail lines
        for i in range(len(self.datalines)):
            self.datalines[i].extend(details[i])

        # load the analysis lines
        service_titles = service_dict.keys()
        service_titles.sort()

        for service_title in service_titles:
            service_uid = analysis_dict[service_title]
            analysis_line = [service_title,]
            for i in range(batch_size):
                if analysis_dict[service_uid].has_key(i):
                    analysis_line.append({'value': analysis_dict[service_uid][i]})
                else:
                    analysis_line.append({})
            self.datalines.extend(analysis_line)



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


