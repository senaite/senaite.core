from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t, dicts_to_dict
from bika.lims.utils \
    import formatDateQuery, formatDateParms, isAttributeHidden
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class Report(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/report_out.pt")

    def __init__(self, context, request, report=None):
        self.report = report
        BrowserView.__init__(self, context, request)

    def __call__(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        self.report_content = {}
        parms = []
        headings = {}
        headings['header'] = _("Analyses out of range")
        headings['subheader'] = _("Analyses results out of specified range")

        count_all = 0

        query = {"portal_type": "Analysis",
                 "sort_order": "reverse"}

        spec_uid = self.request.form.get("spec", False)
        spec_obj = None
        spec_title = ""
        if spec_uid:
            brains = bsc(UID=spec_uid)
            if brains:
                spec_obj = brains[0].getObject()
                spec_title = spec_obj.Title()
        parms.append(
            {"title": _("Range spec"),
             "value": spec_title,
             "type": "text"})

        date_query = formatDateQuery(self.context, 'Received')
        if date_query:
            query['getDateReceived'] = date_query
            received = formatDateParms(self.context, 'Received')
        else:
            received = 'Undefined'
        parms.append(
            {'title': _('Received'),
             'value': received,
             'type': 'text'})

        wf_tool = getToolByName(self.context, 'portal_workflow')
        if self.request.form.has_key('bika_analysis_workflow'):
            query['review_state'] = self.request.form['bika_analysis_workflow']
            review_state = wf_tool.getTitleForStateOnType(
                self.request.form['bika_analysis_workflow'], 'Analysis')
        else:
            review_state = 'Undefined'
        parms.append(
            {'title': _('Status'),
             'value': review_state,
             'type': 'text'})

        if self.request.form.has_key('bika_cancellation_workflow'):
            query['cancellation_state'] = self.request.form[
                'bika_cancellation_workflow']
            cancellation_state = wf_tool.getTitleForStateOnType(
                self.request.form['bika_cancellation_workflow'], 'Analysis')
        else:
            cancellation_state = 'Undefined'
        parms.append(
            {'title': _('Active'),
             'value': cancellation_state,
             'type': 'text'})

        if self.request.form.has_key('bika_worksheetanalysis_workflow'):
            query['worksheetanalysis_review_state'] = self.request.form[
                'bika_worksheetanalysis_workflow']
            ws_review_state = wf_tool.getTitleForStateOnType(
                self.request.form['bika_worksheetanalysis_workflow'], 'Analysis')
        else:
            ws_review_state = 'Undefined'
        parms.append(
            {'title': _('Assigned to worksheet'),
             'value': ws_review_state,
             'type': 'text'})

        # and now lets do the actual report lines
        col_heads = [_('Client'),
                     _('Request'),
                     _('Sample type'),
                     _('Sample point'),
                     _('Category'),
                     _('Analysis'),
                     _('Result'),
                     _('Min'),
                     _('Max'),
                     _('Status'),
        ]
        if isAttributeHidden('Sample', 'SamplePoint'):
            col_heads.remove(_('Sample point'))

        formats = {'columns': 10,
                   'col_heads': col_heads,
                   'class': '',
        }

        datalines = []

        for a_proxy in bac(query):
            analysis = a_proxy.getObject()
            if analysis.getResult():
                try:
                    result = float(analysis.getResult())
                except:
                    continue
            else:
                continue

            keyword = analysis.getKeyword()

            # determine which specs to use for this particular analysis
            # 1) if a spec is given in the query form, use it.
            # 2) if a spec is entered directly on the analysis, use it.
            # otherwise just continue to the next object.
            spec_dict = False
            if spec_obj:
                rr = spec_obj.getResultsRangeDict()
                if keyword in rr:
                    spec_dict = rr[keyword]
            else:
                ar = analysis.aq_parent
                rr = dicts_to_dict(ar.getResultsRange(), 'keyword')
                if keyword in rr:
                    spec_dict = rr[keyword]
                else:
                    continue
            if not spec_dict:
                continue
            try:
                spec_min = float(spec_dict['min'])
                spec_max = float(spec_dict['max'])
            except ValueError:
                continue
            if spec_min <= result <= spec_max:
                continue

            # check if in shoulder: out of range, but in acceptable
            # error percentage
            shoulder = False
            error = 0
            try:
                error = float(spec_dict.get('error', '0'))
            except:
                error = 0
                pass
            error_amount = (result / 100) * error
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

            if isAttributeHidden('Sample', 'SamplePoint'):
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

            dataitem = {'value': spec_dict['min']}
            dataline.append(dataitem)

            dataitem = {'value': spec_dict['max']}
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

        title = t(headings['header'])

        return {'report_title': title,
                'report_data': self.template()}


