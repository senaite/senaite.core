from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.client import ClientSamplesView
from bika.lims.utils import formatDateQuery, formatDateParms, \
                logged_in_client, TimeOrDate
from bika.lims.interfaces import IQueries
from plone.app.content.browser.interfaces import IFolderContentsView
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
        parms = []
        headings = {}
        headings['header'] = _("Analysis Requests")
        headings['subheader'] = _("Selected on the following criteria")

        count_all = 0
        query = {'portal_type': 'AnalysisRequest'}

        if self.request.form.has_key('getClientUID'):
            client_uid = self.request.form['getClientUID']
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
        parms.append(
            { 'title': _('Client'),
             'value': client_title,
             'type': 'text'})

        if self.request.form.has_key('getContactUID'):
            contact_uid = self.request.form['getContactUID']
            query['getContactUID'] = contact_uid
            contact = rc.lookupObject(contact_uid)
            contact_name = contact.getFullname()
        else:
            contact_name = 'Undefined'
        parms.append(
            { 'title': _('Contact'),
             'value': contact_name,
             'type': 'text'})

        if self.request.form.has_key('getAnalysisProfileUID'):
            profile_uid = self.request.form['getAnalysisProfileUID']
            query['getAnalysisProfileUID'] = profile_uid
            profile = rc.lookupObject(profile_uid)
            profile_title = profile.Title()
        else:
            profile_title = 'Undefined'
        parms.append(
            { 'title': _('Profile'),
             'value': profile_title,
             'type': 'text'})

        if self.request.form.has_key('RequestID'):
            request_id = self.request.form['RequestID']
            query['getRequestID'] = request_id
        else:
            request_id = 'Undefined'
        parms.append(
            { 'title': _('AR'),
             'value': request_id,
             'type': 'text'})

        if self.request.form.has_key('ClientOrderNumber'):
            clientordernumber = self.request.form['ClientOrderNumber']
            query['getClientOrderNumber'] = clientordernumber
        else:
            clientordernumber = 'Undefined'
        parms.append(
            { 'title': _('Client order number'),
             'value': clientordernumber,
             'type': 'text'})

        if self.request.form.has_key('ClientReference'):
            clientref = self.request.form['ClientReference']
            query['getClientReference'] = clientref
        else:
            clientref = 'Undefined'
        parms.append(
            { 'title': _('Client reference'),
             'value': clientref,
             'type': 'text'})

        if self.request.form.has_key('ClientSampleID'):
            clientsid = self.request.form['ClientSampleID']
            query['getClientSampleID'] = clientsid
        else:
            clientsid = 'Undefined'
        parms.append(
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
        parms.append(
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
        parms.append(
            { 'title': _('Sample point'),
             'value': sp_title,
             'type': 'text'})

        date_query = formatDateQuery(self.context, 'DateSampled')
        if date_query:
            query['created'] = date_query
            sampled = formatDateParms(self.context, 'DateSampled') 
        else:
            sampled = 'Undefined'
        parms.append(
            { 'title': _('Sampled'),
             'value': sampled,
             'type': 'text'})

        date_query = formatDateQuery(self.context, 'DateRequested')
        if date_query:
            query['created'] = date_query
            requested = formatDateParms(self.context, 'DateRequested') 
        else:
            requested = 'Undefined'
        parms.append(
            { 'title': _('Requested'),
             'value': requested,
             'type': 'text'})

        date_query = formatDateQuery(self.context, 'DateReceived')
        if date_query:
            query['created'] = date_query
            received = formatDateParms(self.context, 'DateReceived') 
        else:
            received = 'Undefined'
        parms.append(
            { 'title': _('Received'),
             'value': received,
             'type': 'text'})

        date_query = formatDateQuery(self.context, 'DatePublished')
        if date_query:
            query['getDatePublished'] = date_query
            published = formatDateParms(self.context, 'DatePublished') 
        else:
            published = 'Undefined'
        parms.append(
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
        parms.append(
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
        parms.append(
            { 'title': _('Analysis service'),
             'value': service_title,
             'type': 'text'})

        if self.request.form.has_key('SubmittedByUID'):
            submittedby_uid = self.request.form['SubmittedByUID']
            query['getSubmittedByUID'] = submittedby_uid
            submittedby = rc.lookupObject(submittedby_uid)
            submittedby_name = submittedby.prettyNameOrTitle()
        else:
            submittedby_name = 'Undefined'
        parms.append(
            { 'title': _('Submitted by'),
             'value': submittedby_name,
             'type': 'text'})

        workflow = getToolByName(self.context, 'portal_workflow')
        if self.request.form.has_key('review_state'):
            query['review_state'] = self.request.form['review_state']
            review_state = workflow.getTitleForStateOnType(
                        self.request.form['review_state'], 'Analysis')
        else:
            review_state = 'Undefined'
        parms.append(
            { 'title': _('Status'),
             'value': review_state,
             'type': 'text'})

        if self.request.form.has_key('cancellation_state'):
            query['cancellation_state'] = self.request.form['cancellation_state']
            cancellation_state = workflow.getTitleForStateOnType(
                        self.request.form['cancellation_state'], 'Analysis')
        else:
            cancellation_state = 'Undefined'
        parms.append(
            { 'title': _('Active'),
             'value': cancellation_state,
             'type': 'text'})



        if self.request.form.has_key('ws_review_state'):
            query['worksheetanalysis_review_state'] = self.request.form['ws_review_state']
            ws_review_state = workflow.getTitleForStateOnType(
                        self.request.form['ws_review_state'], 'Analysis')
        else:
            ws_review_state = 'Undefined'
        parms.append(
            { 'title': _('Assigned to worksheet'),
             'value': ws_review_state,
             'type': 'text'})


        # and now lets do the actual query lines
        formats = {'columns': 7,
                   'col_heads': [], 
                   'class': '',
                  }

        columns = 6
        
        datalines = []
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
        for arp in bc(query):
            ar = arp.getObject()
            clientoid.append({'value': ar.getClientOrderNumber()})
            clientref.append({'value': ar.getClientReference()})
            clientsid.append({'value': ar.getClientSampleID()})
            client.append({'value': ar.aq_parent.Title()})
            contact.append({'value': ar.getContact().Title()})
            requestid.append({'value': ar.getRequestID()})
            sampleid.append({'value': ar.getSample().getSampleID()})
            profile.append({'value': ar.getProfile() and ar.getProfile().Title() or ' '})
            sampletype.append({'value': ar.getSampleTypeTitle()})
            samplepoint.append({'value': ar.getSamplePointTitle()})
            sampled.append({'value': TimeOrDate(self.context, ar.getSample().getDateSampled())})
            requested.append({'value': ' '})
            #requested.append({'value': TimeOrDate(self.context, ar.created())})
            received.append({'value': TimeOrDate(self.context, ar.getDateReceived())})
            published.append({'value': TimeOrDate(self.context, ar.getDatePublished())})
            status.append({'value': ' '})
            #status.append({'value': ar.review_state()})
            submittedby.append({'value': ' '})
            #submittedby.append({'value': ar.getSubmittedBy().Title()})
            verifiedby.append({'value': ' '})
            #verifiedby.append({'value': ar.get_verifier().Title()})
            if len(clientoid) > columns:
                datalines.append(clientoid)
                datalines.append(clientref)
                datalines.append(clientsid)
                datalines.append(client)
                datalines.append(contact)
                datalines.append(requestid)
                datalines.append(sampleid)
                datalines.append(profile)
                datalines.append(sampletype)
                datalines.append(samplepoint)
                datalines.append(sampled)
                datalines.append(requested)
                datalines.append(received)
                datalines.append(published)
                datalines.append(status)
                datalines.append(submittedby)
                datalines.append(verifiedby)
                     

        # footer data
        footlines = []
        footline = []
        footitem = {'value': _('Total'),
                    'class': 'total_label'} 
        footline.append(footitem)
        footitem = {'value': count_all} 
        footline.append(footitem)
        footlines.append(footline)
        

        self.query_content = {
                'headings': headings,
                'parms': parms,
                'formats': formats,
                'datalines': datalines,
                'footings': footlines}


        return self.template()

    
