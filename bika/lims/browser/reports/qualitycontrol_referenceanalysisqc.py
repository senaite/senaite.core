import json
import tempfile

from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t, isAttributeHidden
from bika.lims.browser import BrowserView
from bika.lims.browser.reports.selection_macros import SelectionMacrosView
from gpw import plot
from bika.lims.utils import to_utf8
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import os
import plone


class Report(BrowserView):
    implements(IViewView)

    template = ViewPageTemplateFile(
        "templates/qualitycontrol_referenceanalysisqc.pt")
    # if unsuccessful we return here:
    default_template = ViewPageTemplateFile("templates/qualitycontrol.pt")

    def __init__(self, context, request, report=None):
        super(Report, self).__init__(context, request)
        self.report = report
        self.selection_macros = SelectionMacrosView(self.context, self.request)

    def __call__(self):

        header = _("Reference analysis QC")
        subheader = _("Reference analysis quality control graphs ")

        MinimumResults = self.context.bika_setup.getMinimumResults()

        warning_icon = "<img src='" + self.portal_url + "/++resource++bika.lims.images/warning.png' height='9' width='9'/>"
        error_icon = "<img src='" + self.portal_url + "/++resource++bika.lims.images/exclamation.png' height='9' width='9'/>"

        self.parms = []
        titles = []

        sample_uid = self.request.form.get('ReferenceSampleUID', '')
        sample = self.reference_catalog.lookupObject(sample_uid)
        if not sample:
            message = _("No reference sample was selected.")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.default_template()

        self.parms.append(
            {'title': _("Reference Sample"), 'value': sample.Title()})
        titles.append(sample.Title())

        service_uid = self.request.form.get('ReferenceServiceUID', '')
        service = self.reference_catalog.lookupObject(service_uid)
        if not service:
            message = _("No analysis services were selected.")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.default_template()

        self.contentFilter = {'portal_type': 'ReferenceAnalysis',
                              'review_state': ['verified', 'published'],
                              'path': {
                              "query": "/".join(sample.getPhysicalPath()),
                              "level": 0}}

        self.parms.append(
            {'title': _("Analysis Service"), 'value': service.Title()})
        titles.append(service.Title())

        val = self.selection_macros.parse_daterange(self.request,
                                                    'getDateVerified',
                                                    'DateVerified')
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            self.parms.append(val['parms'])
            titles.append(val['titles'])

        proxies = self.bika_analysis_catalog(self.contentFilter)
        if not proxies:
            message = _("No analyses matched your query")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.default_template()

        # Compile a list with all relevant analysis data
        analyses = []

        out_of_range_count = 0
        results = []
        capture_dates = []

        plotdata = ""
        tabledata = []

        for analysis in proxies:
            analysis = analysis.getObject()
            service = analysis.getService()
            resultsrange = \
            [x for x in sample.getReferenceResults() if x['uid'] == service_uid][
                0]
            try:
                result = float(analysis.getResult())
                results.append(result)
            except:
                result = analysis.getResult()
            capture_dates.append(analysis.getResultCaptureDate())

            if result < float(resultsrange['min']) or result > float(
                    resultsrange['max']):
                out_of_range_count += 1

            try:
                precision = str(analysis.getPrecision())
            except:
                precision = "2"

            try:
                formatted_result = str("%." + precision + "f") % result
            except:
                formatted_result = result

            tabledata.append({_("Analysis"): analysis.getId(),
                              _("Result"): formatted_result,
                              _("Analyst"): analysis.getAnalyst(),
                              _(
                                  "Captured"): analysis.getResultCaptureDate().strftime(
                                  self.date_format_long)})

            plotdata += "%s\t%s\t%s\t%s\n" % (
                analysis.getResultCaptureDate().strftime(self.date_format_long),
                result,
                resultsrange['min'],
                resultsrange['max']
            )
        plotdata.encode('utf-8')

        result_values = [int(r) for r in results]
        result_dates = [c for c in capture_dates]

        self.parms += [
            {"title": _("Total analyses"), "value": len(proxies)},
        ]

        # # This variable is output to the TAL
        self.report_data = {
            'header': header,
            'subheader': subheader,
            'parms': self.parms,
            'tables': [],
            'footnotes': [],
        }

        if MinimumResults <= len(proxies):
            plotscript = """
            set terminal png transparent truecolor enhanced size 700,350 font "Verdana, 8"
            set title "%(title)s"
            set xlabel "%(xlabel)s"
            set ylabel "%(ylabel)s"
            set key off
            #set logscale
            set timefmt "%(timefmt)s"
            set xdata time
            set format x "%(xformat)s"
            set xrange ["%(x_start)s":"%(x_end)s"]
            set auto fix
            set offsets graph 0, 0, 1, 1
            set xtics border nomirror rotate by 90 font "Verdana, 5" offset 0,-3
            set ytics nomirror

            f(x) = mean_y
            fit f(x) 'gpw_DATAFILE_gpw' u 1:3 via mean_y
            stddev_y = sqrt(FIT_WSSR / (FIT_NDF + 1))

            plot mean_y-stddev_y with filledcurves y1=mean_y lt 1 lc rgb "#efefef",\
                 mean_y+stddev_y with filledcurves y1=mean_y lt 1 lc rgb "#efefef",\
                 mean_y with lines lc rgb '#ffffff' lw 3,\
                 "gpw_DATAFILE_gpw" using 1:3 title 'data' with points pt 7 ps 1 lc rgb '#0000ee' lw 2,\
                   '' using 1:3 smooth unique lc rgb '#aaaaaa' lw 2,\
                   '' using 1:4 with lines lc rgb '#000000' lw 1,\
                   '' using 1:5 with lines lc rgb '#000000' lw 1""" % \
                         {
                             'title': "",
                             'xlabel': "",
                             'ylabel': service.getUnit(),
                             'x_start': "%s" % min(result_dates).strftime(
                                 self.date_format_short),
                             'x_end': "%s" % max(result_dates).strftime(
                                 self.date_format_short),
                             'timefmt': r'%Y-%m-%d %H:%M',
                             'xformat': '%%Y-%%m-%%d\n%%H:%%M',
                         }

            plot_png = plot(str(plotdata), plotscript=str(plotscript),
                            usefifo=False)

            # Temporary PNG data file
            fh, data_fn = tempfile.mkstemp(suffix='.png')
            os.write(fh, plot_png)
            plot_url = data_fn
            self.request['to_remove'].append(data_fn)
            plot_url = data_fn
        else:
            plot_url = ""

        table = {
            'title': "%s: %s (%s)" % (
                t(_("Analysis Service")),
                service.Title(),
                service.getKeyword()
            ),
            'columns': [_('Analysis'),
                        _('Result'),
                        _('Analyst'),
                        _('Captured')],
            'parms': [],
            'data': tabledata,
            'plot_url': plot_url,
        }

        self.report_data['tables'].append(table)

        translate = self.context.translate

        ## footnotes
        if out_of_range_count:
            msgid = _("Analyses out of range")
            self.report_data['footnotes'].append(
                "%s %s" % (error_icon, t(msgid)))

        self.report_data['parms'].append(
            {"title": _("Analyses out of range"),
             "value": out_of_range_count})

        title = t(header)
        if titles:
            title += " (%s)" % " ".join(titles)
        return {
            'report_title': title,
            'report_data': self.template(),
        }

    def isSamplePointHidden(self):
        return isAttributeHidden('AnalysisRequest', 'SamplePoint')
