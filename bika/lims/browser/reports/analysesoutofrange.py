from AccessControl import getSecurityManager
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

class AnalysesOutOfRange(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/report_out.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        self.report_content = {}
        parm_lines = {}
        parms = []
        headings = {}
        headings['header'] = _("Analyses out of range")
        headings['subheader'] = _("Analyses results out of client or lab specified range")

        count_all = 0

        query = {'portal_type': 'Analysis',
                 'sort_order': 'reverse'}

        if self.request.form.has_key('spec'):
            spec = self.request.form['spec']
        else:
            spec = 'lab'
        if spec == 'lab':
            lab_spec = True
        else:
            lab_spec = False

        parms.append(
            { 'title': _('Range spec'),
             'value': spec,
             'type': 'text'})

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
        formats = {'columns': 10,
                   'col_heads': [ _('Client'), \
                                  _('Request'), \
                                  _('Sample type'), \
                                  _('Sample point'), \
                                  _('Category'), \
                                  _('Analysis'), \
                                  _('Result'), \
                                  _('Min'), \
                                  _('Max'), \
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
        specs = {}

        if lab_spec:
            owner_uid = self.context.bika_setup.bika_analysisspecs.UID()

        for a_proxy in bac(query):
            analysis = a_proxy.getObject()
            if analysis.getResult():
                try:
                    result = float(analysis.getResult())
                except:
                    continue
            else:
                continue

            sampletypeuid = analysis.getSampleTypeUID()

            # determine which specs to use, and load if not yet found
            if not lab_spec:
                owner_uid = analysis.getClientUID()
            if not specs.has_key(owner_uid):
                specs[owner_uid] = {}
            if not specs[owner_uid].has_key(sampletypeuid):
                proxies = bsc(portal_type = 'AnalysisSpec',
                              getSampleTypeUID = sampletypeuid,
                              getClientUID = owner_uid)
                if len(proxies) == 0:
                    continue
                spec_object = proxies[0].getObject()
                specs[owner_uid][sampletypeuid] = spec_object.getResultsRangeDict()
            spec = specs[owner_uid][sampletypeuid]

            keyword = analysis.getKeyword()
            if spec.has_key(keyword):
                spec_min = float(spec[keyword]['min'])
                spec_max = float(spec[keyword]['max'])
                if spec_min <= result <= spec_max:
                    continue
            else:
                continue

            # check if in shoulder: out of range, but in acceptable
            #     error percentage
            shoulder = False
            error_amount = (result / 100) * float(spec[keyword]['error'])
            error_min = result - error_amount
            error_max = result + error_amount
            if ((result < spec_min) and (error_max >= spec_min)) or \
               ((result > spec_max) and (error_min <= spec_max)):
                shoulder = True



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

            if shoulder:
                dataitem = {'value': analysis.getResult(),
                            'img_after': '++resource++bika.lims.images/exclamation.png'}
            else:
                dataitem = {'value': analysis.getResult()}

            dataline.append(dataitem)

            dataitem = {'value': spec[keyword]['min']}
            dataline.append(dataitem)

            dataitem = {'value': spec[keyword]['max']}
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
        footitem = {'value': _('Number of analyses out of range for period'),
                    'colspan': 9,
                    'class': 'total_label'}
        footline.append(footitem)
        footitem = {'value': count_all}
        footline.append(footitem)
        footlines.append(footline)

        # report footer data
        footnotes = []
        footline = []
        footitem = {'value': _('Analysis result within error range'),
                    'img_before': '++resource++bika.lims.images/exclamation.png'
                   }
        footline.append(footitem)
        footnotes.append(footline)



        self.report_content = {
                'headings': headings,
                'parms': parms,
                'formats': formats,
                'datalines': datalines,
                'footings': footlines,
                'footnotes': footnotes}


        return self.template()



