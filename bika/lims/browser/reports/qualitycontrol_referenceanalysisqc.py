from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.reports.selection_macros import SelectionMacrosView
from gpw import plot
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json
import os
import plone
import tempfile

class Report(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/qualitycontrol_referenceanalysisqc.pt")
    # if unsuccessful we return here:
    default_template = ViewPageTemplateFile("templates/qualitycontrol.pt")

    def __init__(self, context, request, report=None):
        super(Report, self).__init__(context, request)
        self.report = report
        self.selection_macros = SelectionMacrosView(self.context, self.request)

    def __call__(self):
        MinimumResults = self.context.bika_setup.getMinimumResults()
        warning_icon = "<img " +\
            "src='"+self.portal_url+"/++resource++bika.lims.images/warning.png' " +\
            "height='9' width='9'/>"
        error_icon = "<img " +\
            "src='"+self.portal_url+"/++resource++bika.lims.images/exclamation.png' " +\
            "height='9' width='9'/>"

        header = _("Reference analysis QC")
        subheader = _("Reference analysis quality control graphs ")

        self.contentFilter = {'portal_type': 'ReferenceAnalysis',
                              'review_state': ['verified', 'published'],
                              }

        self.parms = []
        titles = []

        sample_uid = self.request.form.get('ReferenceSampleUID', '')
        sample = self.reference_catalog.lookupObject(sample_uid)
        if not sample:
            message = _("No reference sample was selected.")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.default_template()
        self.parms.append({'title':_("Reference Sample"),'value':sample.Title()})
        titles.append(sample.Title())

        service_uid = self.request.form.get('ReferenceServiceUID', '')
        service = self.reference_catalog.lookupObject(service_uid)
        if not service:
            message = _("No analysis services were selected.")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.default_template()

        self.contentFilter['path'] = {"query": "/".join(sample.getPhysicalPath()),
                                      "level" : 0 }
        keyword = service.getKeyword()
        unit = service.getUnit()
        service_title = "%s (%s)" % (service.Title(), service.getKeyword())
        try:
            precision = str(service.getPrecision())
        except:
            precision = "2"
        self.parms.append({'title':_("Analysis Service"),'value':service.Title()})
        titles.append(service.Title())

        val = self.selection_macros.parse_daterange(self.request,
                                                    'getDateVerified',
                                                    'DateVerified')
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            self.parms.append(val['parms'])
            titles.append(val['titles'])

        # GET min/max for range checking

        proxies = self.bika_analysis_catalog(self.contentFilter)
        if not proxies:
            message = _("No analyses matched your query")
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.default_template()

        ## Compile a list with all relevant analysis data
        analyses = []
        out_of_range_count = 0
        in_shoulder_range_count = 0
        plot_data = ""
        formatted_results = []
        results = []
        tabledata = []

        for analysis in proxies:
            analysis = analysis.getObject()
            analyses.append(analysis)
            try:
                result = float(analysis.getResult())
            except ValueError:
                pass
            results.append(result)
            captured = self.ulocalized_time(analysis.getResultCaptureDate(), long_format=1)
            analyst = analysis.getAnalyst()
            title = analysis.getId()
            formatted_result = str("%." + precision + "f")%result
            formatted_results.append(formatted_result)
            tabledata.append({_("Analysis"): title,
                              _("Result"): formatted_result,
                              _("Analyst"): analyst,
                              _("Captured"): captured})
        plotdata = "\n".join(formatted_results)
        plotdata.encode('utf-8')

        ### CHECK RANGES

        self.parms += [
            {"title": _("Total analyses"), "value": len(analyses)},
        ]

        ## This variable is output to the TAL
        self.report_data = {
            'header': header,
            'subheader': subheader,
            'parms': self.parms,
            'tables': [],
            'footnotes': [],
        }

        plotscript = """
        set terminal png transparent truecolor enhanced size 700,350 font "Verdana, 8"
        set title "%(title)s"
        set xlabel "%(xlabel)s"
        set ylabel "%(ylabel)s"
        set yzeroaxis
        #set logscale
        set xrange [highest:lowest]
        set xtics border nomirror rotate by 90 font "Verdana, 5" offset 0,-3
        set ytics nomirror

        binwidth = %(highest)-%(lowest)/100
        scale = (binwidth/(%(highest)-%(lowest)))

        bin_number(x) = floor(x/binwidth)
        rounded(x) = binwidth * ( binnumber(x) + 0.5 )

        #f(x) = mean_x
        #fit f(x) 'gpw_DATAFILE_gpw' u 1:2 via mean_x
        #stddev_x = sqrt(FIT_WSSR / (FIT_NDF + 1))
        #
        #plot mean_y-stddev_y with lines y1=mean_y lt 1 lc rgb "#afafaf",\
        #     mean_y+stddev_y with lines y1=mean_y lt 1 lc rgb "#afafaf",\
        #     mean_y with lines lc rgb '#000000' lw 1,\
        plot "gpw_DATAFILE_gpw" using (rounded($1)):(1) smooth frequency
        """

        if MinimumResults <= len(analyses):
            _plotscript = str(plotscript)%\
            {'title': "",
             'xlabel': "",
             'ylabel': "",
             'highest': max(results),
             'lowest': min(results)}

            plot_png = plot(str(plotdata),
                                plotscript=str(_plotscript),
                                usefifo=False)

            print plotdata
            print _plotscript
            print "-------"

            # Temporary PNG data file
            fh,data_fn = tempfile.mkstemp(suffix='.png')
            os.write(fh, plot_png)
            plot_url = data_fn
            self.request['to_remove'].append(data_fn)

            plot_url = data_fn
        else:
            plot_url = ""

        table = {
            'title': "%s: %s" % (
                self.context.translate(_("Analysis Service")),
                service_title),
            'columns': [_('Analysis'),
                        _('Result'),
                        _('Analyst'),
                        _('Captured')],
            'parms':[],
            'data': tabledata,
            'plot_url': plot_url,
        }

        self.report_data['tables'].append(table)

        ## footnotes
        if out_of_range_count:
            msgid = _("Analyses out of range")
            translate = self.context.translate
            self.report_data['footnotes'].append(
                "%s %s" % (error_icon, translate(msgid)))
        if in_shoulder_range_count:
            msgid = _("Analyses in error shoulder range")
            self.report_data['footnotes'].append(
                "%s %s" % (warning_icon, translate(msgid)))

        self.report_data['parms'].append(
            {"title": _("Analyses out of range"),
             "value": out_of_range_count})
        self.report_data['parms'].append(
            {"title": _("Analyses in error shoulder range"),
             "value": in_shoulder_range_count})

        title = self.context.translate(header)
        if titles:
            title += " (%s)" % " ".join(titles)
        return {
            'report_title': title,
            'report_data': self.template(),
        }
