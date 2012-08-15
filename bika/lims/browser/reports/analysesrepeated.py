from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.client import ClientSamplesView
from bika.lims.utils import formatDateQuery, formatDateParms, TimeOrDate
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json
import plone

class AnalysesRepeated(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/report_out.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        self.report_content = {}
        parm_lines = {}
        parms = []
        headings = {}
        headings['header'] = _("Analyses retested")
        headings['subheader'] = _("Analyses which have been retested")

        count_all = 0

        query = {'portal_type': 'Analysis',
                 'getRetested': True,
                 'sort_order': 'reverse'}

        date_query = formatDateQuery(self.context, 'c_DateReceived')
        if date_query:
            query['getDateReceived'] = date_query
            received = formatDateParms(self.context, 'c_DateReceived')
        else:
            received = 'Undefined'
        parms.append(
            { 'title': _('Received'),
             'value': received,
             'type': 'text'})

        wf_tool = getToolByName(self.context, 'portal_workflow')
        if self.request.form.has_key('review_state'):
            query['review_state'] = self.request.form['review_state']
            review_state = wf_tool.getTitleForStateOnType(
                        self.request.form['review_state'], 'Analysis')
        else:
            review_state = 'Undefined'
        parms.append(
            { 'title': _('Status'),
             'value': review_state,
             'type': 'text'})

        if self.request.form.has_key('cancellation_state'):
            query['cancellation_state'] = self.request.form['cancellation_state']
            cancellation_state = wf_tool.getTitleForStateOnType(
                        self.request.form['cancellation_state'], 'Analysis')
        else:
            cancellation_state = 'Undefined'
        parms.append(
            { 'title': _('Active'),
             'value': cancellation_state,
             'type': 'text'})


        if self.request.form.has_key('ws_review_state'):
            query['worksheetanalysis_review_state'] = self.request.form['ws_review_state']
            ws_review_state = wf_tool.getTitleForStateOnType(
                        self.request.form['ws_review_state'], 'Analysis')
        else:
            ws_review_state = 'Undefined'
        parms.append(
            { 'title': _('Assigned to worksheet'),
             'value': ws_review_state,
             'type': 'text'})


        # and now lets do the actual report lines
        formats = {'columns': 8,
                   'col_heads': [ _('Client'), \
                                  _('Request'), \
                                  _('Sample type'), \
                                  _('Sample point'), \
                                  _('Category'), \
                                  _('Analysis'), \
                                  _('Received'), \
                                  _('Status'), \
                                  ],
                   'class': '',
                  }

        datalines = []
        clients = {}
        sampletypes = {}
        samplepoints = {}
        categories = {}
        services = {}

        for a_proxy in bac(query):
            analysis = a_proxy.getObject()

            dataline = []

            dataitem = {'value': analysis.getClientTitle()}
            dataline.append(dataitem)

            dataitem = {'value': analysis.getRequestID()}
            dataline.append(dataitem)

            dataitem = {'value': analysis.aq_parent.getSampleTypeTitle()}
            dataline.append(dataitem)

            dataitem = {'value': analysis.aq_parent.getSamplePointTitle()}
            dataline.append(dataitem)

            dataitem = {'value': analysis.getCategoryTitle()}
            dataline.append(dataitem)

            dataitem = {'value': analysis.getServiceTitle()}
            dataline.append(dataitem)

            dataitem = {'value': TimeOrDate(self.context, analysis.getDateReceived())}
            dataline.append(dataitem)

            state = wf_tool.getInfoFor(analysis, 'review_state', '')
            review_state = wf_tool.getTitleForStateOnType(
                        state, 'Analysis')
            dataitem = {'value': review_state}
            dataline.append(dataitem)


            datalines.append(dataline)

            count_all += 1

        # table footer data
        footlines = []
        footline = []
        footitem = {'value': _('Number of analyses retested for period'),
                    'colspan': 7,
                    'class': 'total_label'}
        footline.append(footitem)
        footitem = {'value': count_all}
        footline.append(footitem)
        footlines.append(footline)


        self.report_content = {
                'headings': headings,
                'parms': parms,
                'formats': formats,
                'datalines': datalines,
                'footings': footlines}


        return self.template()



