from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.reports.selection_macros import SelectionMacrosView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class Report(BrowserView):
    implements(IViewView)
    default_template = ViewPageTemplateFile("templates/productivity.pt")
    template = ViewPageTemplateFile(
        "templates/productivity_dailysamplesreceived.pt")

    def __init__(self, context, request, report=None):
        super(Report, self).__init__(context, request)
        self.report = report
        self.selection_macros = SelectionMacrosView(self.context, self.request)

    def __call__(self):

        parms = []
        titles = []

        self.contentFilter = {'portal_type': 'Sample',
                              'review_state': ['sample_received', 'expired',
                                               'disposed'],
                              'sort_on': 'getDateReceived'}

        val = self.selection_macros.parse_daterange(self.request,
                                                    'getDateReceived',
                                                    _('Date Received'))
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            parms.append(val['parms'])
            titles.append(val['titles'])

        # Query the catalog and store results in a dictionary
        samples = self.bika_catalog(self.contentFilter)
        if not samples:
            message = _("No samples matched your query")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()

        datalines = []
        analyses_count = 0
        for sample in samples:
            sample = sample.getObject()

            # For each sample, retrieve the analyses and generate
            # a data line for each one
            analyses = sample.getAnalyses({})
            for analysis in analyses:
                analysis = analysis.getObject()
                dataline = {'AnalysisKeyword': analysis.getKeyword(),
                            'AnalysisTitle': analysis.getServiceTitle(),
                            'SampleID': sample.getSampleID(),
                            'SampleType': sample.getSampleType().Title(),
                            'SampleDateReceived': self.ulocalized_time(
                                sample.getDateReceived(), long_format=1),
                            'SampleSamplingDate': self.ulocalized_time(
                                sample.getSamplingDate(), long_format=1)}
                datalines.append(dataline)
                analyses_count += 1

        # Footer total data
        footlines = []
        footline = {'TotalCount': analyses_count}
        footlines.append(footline)

        self.report_data = {
            'parameters': parms,
            'datalines': datalines,
            'footlines': footlines}

        if self.request.get('output_format', '') == 'CSV':
            import csv
            import StringIO
            import datetime

            fieldnames = [
                'SampleID',
                'SampleType',
                'SampleSamplingDate',
                'SampleDateReceived',
                'AnalysisTitle',
                'AnalysisKeyword',
            ]
            output = StringIO.StringIO()
            dw = csv.DictWriter(output, fieldnames=fieldnames)
            dw.writerow(dict((fn, fn) for fn in fieldnames))
            for row in datalines:
                dw.writerow(row)
            report_data = output.getvalue()
            output.close()
            date = datetime.datetime.now().strftime("%Y%m%d%H%M")
            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'text/csv')
            setheader("Content-Disposition",
                      "attachment;filename=\"dailysamplesreceived_%s.csv\"" % date)
            self.request.RESPONSE.write(report_data)
        else:
            return {'report_title': _('Daily samples received'),
                    'report_data': self.template()}
