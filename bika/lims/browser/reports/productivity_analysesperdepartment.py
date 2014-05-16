from Products.CMFCore.utils import getToolByName
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
        "templates/productivity_analysesperdepartment.pt")

    def __init__(self, context, request, report=None):
        super(Report, self).__init__(context, request)
        self.report = report
        self.selection_macros = SelectionMacrosView(self.context, self.request)

    def __call__(self):

        parms = []
        titles = []

        # Apply filters
        self.contentFilter = {'portal_type': 'Analysis'}
        val = self.selection_macros.parse_daterange(self.request,
                                                    'getDateRequested',
                                                    _('Date Requested'))
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            parms.append(val['parms'])
            titles.append(val['titles'])

        val = self.selection_macros.parse_state(self.request,
                                                'bika_analysis_workflow',
                                                'getAnalysisState',
                                                _('Analysis State'))
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            parms.append(val['parms'])
            titles.append(val['titles'])

        # Query the catalog and store results in a dictionary
        analyses = self.bika_analysis_catalog(self.contentFilter)
        if not analyses:
            message = _("No analyses matched your query")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()

        groupby = self.request.form.get('GroupingPeriod', '')
        if (groupby != ''):
            parms.append({"title": _("Grouping period"), "value": _(groupby)})

        datalines = {}
        footlines = {}
        totalcount = len(analyses)
        totalpublishedcount = 0
        totalperformedcount = 0
        for analysis in analyses:
            analysis = analysis.getObject()
            analysisservice = analysis.getService()
            department = analysisservice.getDepartment()
            department = department.Title() if department else ''
            daterequested = analysis.created()

            group = ''
            if groupby == 'Day':
                group = self.ulocalized_time(daterequested)
            elif groupby == 'Week':
                group = daterequested.strftime(
                    "%Y") + ", " + daterequested.strftime("%U")
            elif groupby == 'Month':
                group = daterequested.strftime(
                    "%B") + " " + daterequested.strftime("%Y")
            elif groupby == 'Year':
                group = daterequested.strftime("%Y")
            else:
                group = ''

            dataline = {'Group': group, 'Requested': 0, 'Performed': 0,
                        'Published': 0, 'Departments': {}}
            deptline = {'Department': department, 'Requested': 0, 'Performed': 0,
                        'Published': 0}
            if (group in datalines):
                dataline = datalines[group]
                if (department in dataline['Departments']):
                    deptline = dataline['Departments'][department]

            grouptotalcount = dataline['Requested'] + 1
            groupperformedcount = dataline['Performed']
            grouppublishedcount = dataline['Published']

            depttotalcount = deptline['Requested'] + 1
            deptperformedcount = deptline['Performed']
            deptpubishedcount = deptline['Published']

            workflow = getToolByName(self.context, 'portal_workflow')
            arstate = workflow.getInfoFor(analysis.aq_parent, 'review_state', '')
            if (arstate == 'published'):
                deptpubishedcount += 1
                grouppublishedcount += 1
                totalpublishedcount += 1

            if (analysis.getResult()):
                deptperformedcount += 1
                groupperformedcount += 1
                totalperformedcount += 1

            group_performedrequested_ratio = float(groupperformedcount) / float(
                grouptotalcount)
            group_publishedperformed_ratio = groupperformedcount > 0 and float(
                grouppublishedcount) / float(groupperformedcount) or 0

            anl_performedrequested_ratio = float(deptperformedcount) / float(
                depttotalcount)
            anl_publishedperformed_ratio = deptperformedcount > 0 and float(
                deptpubishedcount) / float(deptperformedcount) or 0

            dataline['Requested'] = grouptotalcount
            dataline['Performed'] = groupperformedcount
            dataline['Published'] = grouppublishedcount
            dataline['PerformedRequestedRatio'] = group_performedrequested_ratio
            dataline['PerformedRequestedRatioPercentage'] = ('{0:.0f}'.format(
                group_performedrequested_ratio * 100)) + "%"
            dataline['PublishedPerformedRatio'] = group_publishedperformed_ratio
            dataline['PublishedPerformedRatioPercentage'] = ('{0:.0f}'.format(
                group_publishedperformed_ratio * 100)) + "%"

            deptline['Requested'] = depttotalcount
            deptline['Performed'] = deptperformedcount
            deptline['Published'] = deptpubishedcount
            deptline['PerformedRequestedRatio'] = anl_performedrequested_ratio
            deptline['PerformedRequestedRatioPercentage'] = ('{0:.0f}'.format(
                anl_performedrequested_ratio * 100)) + "%"
            deptline['PublishedPerformedRatio'] = anl_publishedperformed_ratio
            deptline['PublishedPerformedRatioPercentage'] = ('{0:.0f}'.format(
                anl_publishedperformed_ratio * 100)) + "%"

            dataline['Departments'][department] = deptline
            datalines[group] = dataline

        # Footer total data
        total_performedrequested_ratio = float(totalperformedcount) / float(
            totalcount)
        total_publishedperformed_ratio = totalperformedcount > 0 and float(
            totalpublishedcount) / float(totalperformedcount) or 0

        footline = {'Requested': totalcount,
                    'Performed': totalperformedcount,
                    'Published': totalpublishedcount,
                    'PerformedRequestedRatio': total_performedrequested_ratio,
                    'PerformedRequestedRatioPercentage': ('{0:.0f}'.format(
                        total_performedrequested_ratio * 100)) + "%",
                    'PublishedPerformedRatio': total_publishedperformed_ratio,
                    'PublishedPerformedRatioPercentage': ('{0:.0f}'.format(
                        total_publishedperformed_ratio * 100)) + "%"}

        footlines['Total'] = footline

        self.report_data = {'parameters': parms,
                            'datalines': datalines,
                            'footlines': footlines}

        if self.request.get('output_format', '') == 'CSV':
            import csv
            import StringIO
            import datetime

            fieldnames = [
                'Group',
                'Department',
                'Requested',
                'Performed',
                'Published',
            ]
            output = StringIO.StringIO()
            dw = csv.DictWriter(output, extrasaction='ignore',
                                fieldnames=fieldnames)
            dw.writerow(dict((fn, fn) for fn in fieldnames))
            for group_name, group in datalines.items():
                for dept_name, dept in group['Departments'].items():
                    dw.writerow({
                        'Group': group_name,
                        'Department': dept_name,
                        'Requested': dept['Requested'],
                        'Performed': dept['Performed'],
                        'Published': dept['Published'],
                    })
            report_data = output.getvalue()
            output.close()
            date = datetime.datetime.now().strftime("%Y%m%d%H%M")
            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'text/csv')
            setheader("Content-Disposition",
                      "attachment;filename=\"analysesperdepartment_%s.csv\"" % date)
            self.request.RESPONSE.write(report_data)
        else:
            return {'report_title': _('Analyses summary per department'),
                    'report_data': self.template()}
