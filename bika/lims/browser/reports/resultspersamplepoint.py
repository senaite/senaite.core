from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.client import ClientSamplesView
from bika.lims.utils import formatDateQuery, formatDateParms, logged_in_client
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json
import plone

class ResultsPerSamplePoint(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("report_out.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        # get all the data into datalines
        
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        localTimeFormat = self.context.portal_properties.site_properties.getProperty('localTimeFormat')
        self.report_content = {}
        parm_lines = {}
        parms = []
        headings = {}
        headings['header'] = _("Results per sample point")
        headings['subheader'] = _("Analysis results per sample point and analysis service")

        count_all = 0

        query = {'portal_type' : "Analysis",
                 'review_state': 'published',
                 'sort_on'     : 'getDateAnalysisPublished'}
                 

        if self.request.form.has_key('getSamplePointUID'):
            sp_uid = self.request.form['getSamplePointUID']
            query['getSamplePointUID'] = sp_uid
            sp = rc.lookupObject(sp_uid)
            sp_title = sp.Title()
        else:
            sp_title = 'Undefined'
        parms.append(
            { 'title': _('Sample point'),
             'value': sp_title,
             'type': 'text'})

        service_uids = []
        if self.request.form.has_key('getServiceUID'):
            service_uid = self.request.form['getServiceUID']
            query['getServiceUID'] = service_uid
        if type(service_uid) == str:
            # a single service was selected
            service_uids.append(service_uid)
            no_services = 1
        else:
            # multiple services were selected
            service_uids = list(service_uid)
            no_services = len(service_uids)

        service_titles = []
        service_values = {}
        service_counts = {}
        service_oor = {}
        for service_uid in service_uids:
            service = rc.lookupObject(service_uid)
            service_titles.append(service.Title())
            service_values[service_uid] = []
            service_counts[service_uid] = 0
            service_oor[service_uid] = 0
         
        
        date_query = formatDateQuery(self.context, 'DateAnalysisPublished')
        if date_query:
            query['getDateAnalysisPublished'] = date_query
            published = formatDateParms(self.context, 'DateAnalysisPublished') 
        else:
            published = 'Undefined'
        parms.append(
            { 'title': _('Published'),
             'value': published,
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


        # and now lets do the actual report lines
        formats = {'columns': no_services + 1,
                   'col_heads': [' ',] + service_titles,
                   'class': '',
                  }

        datalines = []
        dataline = []
        current = None
        for a_proxy in bac(query):
            analysis = a_proxy.getObject()
            pubdate = analysis.getDateAnalysisPublished()
            published = pubdate.strftime('%d%m%YY')
            if published != current:
                # print the previous date
                dataline.append({'value': current})
                for service_uid in service_uids:
                    dataline.append({'value': service_values[service_uid]})
                    service_values[service_uid] = [{'value': '-'},]

                datalines.append(dataline)
                dataline = []
                dataline.append({'value': published})
                current = published
 
            service_values[service_uid].append( \
                {'value': analysis.getResult()})
            service_counts[service_uid] += 1
            #if service.getResult() is outofrange:
            #    service_oor[service_uid] += 1

        # footer data
        footlines = []
        footline = []
        footitem = {'value': _('Total analyses out of range'),
                    'colspan': 1,
                    'class': 'total_label'} 
        footline.append(footitem)
        for service_uid in service_uids:
            #footitem = {'value': service_oor[service_uid]} 
            footitem = {'value': 10} 
            footline.append(footitem)

        footlines.append(footline)

        footline = []
        footitem = {'value': _('Total number of analyses'),
                    'colspan': 1,
                    'class': 'total_label'} 
        footline.append(footitem)
        for service_uid in service_uids:
            footitem = {'value': service_counts[service_uid]} 
            footline.append(footitem)
        footlines.append(footline)

        

        self.report_content = {
                'headings': headings,
                'parms': parms,
                'formats': formats,
                'datalines': datalines,
                'footings': footlines}


        return self.template()

    

