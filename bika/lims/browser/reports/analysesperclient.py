from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.client import ClientSamplesView
from bika.lims.utils import formatDateQuery, formatDateParms, logged_in_client
from bika.lims.interfaces import IReportFolder
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json
import plone

class AnalysesPerClient(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/report_out.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        # get all the data into datalines

        pc = getToolByName(self.context, 'portal_catalog')
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        bc = getToolByName(self.context, 'bika_catalog')

        self.report_content = {}
        parm_lines = {}
        parms = []
        headings = {}
        this_client = logged_in_client(self.context)

        if this_client:
            headings['header'] = _("Analysis requests and analyses")
            headings['subheader'] = _("Number of Analysis requests and analyses")
        else:
            headings['header'] = _("Analysis requests and analyses per client")
            headings['subheader'] = _("Number of Analysis requests and analyses per client")

        count_all_ars = 0
        count_all_analyses = 0
        query = {}

        date_query = formatDateQuery(self.context, 'c_DateRequested')
        if date_query:
            query['created'] = date_query
            requested = formatDateParms(self.context, 'c_DateRequested')
        else:
            requested = 'Undefined'
        parms.append(
            { 'title': _('Requested'),
             'value': requested,
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


        # and now lets do the actual report lines
        formats = {'columns': 3,
                   'col_heads': [ _('Client'), \
                                  _('Number of requests'), \
                                  _('Number of analyses')],
                   'class': '',
                  }

        datalines = []

        if this_client:
            c_proxies = pc(portal_type="Client",
                           UID=this_client.UID())
        else:
            c_proxies = pc(portal_type="Client",
                        sort_on='sortable_title')

        for client in c_proxies:
            query['getClientUID'] = client.UID
            dataline = [{'value': client.Title },]
            query['portal_type'] = 'AnalysisRequest'
            ars = bc(query)
            count_ars = len(ars)
            dataitem = {'value': count_ars}
            dataline.append(dataitem)

            query['portal_type'] = 'Analysis'
            analyses = bac(query)
            count_analyses = len(analyses)
            dataitem = {'value': count_analyses }
            dataline.append(dataitem)


            datalines.append(dataline)

            count_all_analyses += count_analyses
            count_all_ars += count_ars

        # footer data
        footlines = []
        if not this_client:
            footline = []
            footitem = {'value': _('Total'),
                        'class': 'total_label'}
            footline.append(footitem)

            footitem = {'value': count_all_ars}
            footline.append(footitem)
            footitem = {'value': count_all_analyses}
            footline.append(footitem)

            footlines.append(footline)


        self.report_content = {
                'headings': headings,
                'parms': parms,
                'formats': formats,
                'datalines': datalines,
                'footings': footlines}


        return self.template()



