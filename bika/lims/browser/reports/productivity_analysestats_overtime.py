from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.utils import formatDateQuery, formatDateParms, formatDuration
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class Report(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/report_out.pt")

    def __init__(self, context, request, report=None):
        self.report = report
        BrowserView.__init__(self, context, request)

    def __call__(self):
        # get all the data into datalines

        bc = getToolByName(self.context, 'bika_analysis_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        self.report_content = {}
        parms = []
        headings = {}
        headings['header'] = _("Analysis turnaround times over time")
        headings['subheader'] = \
            _("The turnaround time of analyses plotted over time")

        query = {'portal_type': 'Analysis'}

        if 'ServiceUID' in self.request.form:
            service_uid = self.request.form['ServiceUID']
            query['ServiceUID'] = service_uid
            service = rc.lookupObject(service_uid)
            service_title = service.Title()
            parms.append(
                {'title': _('Analysis Service'),
                 'value': service_title,
                 'type': 'text'})

        if 'Analyst' in self.request.form:
            analyst = self.request.form['Analyst']
            query['getAnalyst'] = analyst
            analyst_title = self.user_fullname(analyst)
            parms.append(
                {'title': _('Analyst'),
                 'value': analyst_title,
                 'type': 'text'})

        if 'getInstrumentUID' in self.request.form:
            instrument_uid = self.request.form['getInstrumentUID']
            query['getInstrument'] = instrument_uid
            instrument = rc.lookupObject(instrument_uid)
            instrument_title = instrument.Title()
            parms.append(
                {'title': _('Instrument'),
                 'value': instrument_title,
                 'type': 'text'})

        if 'Period' in self.request.form:
            period = self.request.form['Period']
        else:
            period = 'Day'

        date_query = formatDateQuery(self.context, 'tats_DateReceived')
        if date_query:
            query['created'] = date_query
            received = formatDateParms(self.context, 'tats_DateReceived')
            parms.append(
                {'title': _('Received'),
                 'value': received,
                 'type': 'text'})

        query['review_state'] = 'published'

        # query all the analyses and increment the counts

        periods = {}
        total_count = 0
        total_duration = 0

        analyses = bc(query)
        for a in analyses:
            analysis = a.getObject()
            received = analysis.created()
            if period == 'Day':
                datekey = received.strftime('%d %b %Y')
            elif period == 'Week':
                # key period on Monday
                dayofweek = received.strftime('%w')  # Sunday = 0
                if dayofweek == 0:
                    firstday = received - 6
                else:
                    firstday = received - (int(dayofweek) - 1)
                datekey = firstday.strftime(self.date_format_short)
            elif period == 'Month':
                datekey = received.strftime('%m-%d')
            if datekey not in periods:
                periods[datekey] = {'count': 0,
                                    'duration': 0,
                }
            count = periods[datekey]['count']
            duration = periods[datekey]['duration']
            count += 1
            duration += analysis.getDuration()
            periods[datekey]['duration'] = duration
            periods[datekey]['count'] = count
            total_count += 1
            total_duration += duration

        # calculate averages
        for datekey in periods.keys():
            count = periods[datekey]['count']
            duration = periods[datekey]['duration']
            ave_duration = (duration) / count
            periods[datekey]['duration'] = \
                formatDuration(self.context, ave_duration)

        # and now lets do the actual report lines
        formats = {'columns': 2,
                   'col_heads': [_('Date'),
                                 _('Turnaround time (h)'),
                   ],
                   'class': '',
        }

        datalines = []

        period_keys = periods.keys()
        for period in period_keys:
            dataline = [{'value': period,
                         'class': ''}, ]
            dataline.append({'value': periods[period]['duration'],
                             'class': 'number'})
            datalines.append(dataline)

        if total_count > 0:
            ave_total_duration = total_duration / total_count
        else:
            ave_total_duration = 0
        ave_total_duration = formatDuration(self.context, ave_total_duration)

        # footer data
        footlines = []
        footline = []
        footline = [{'value': _('Total data points'),
                     'class': 'total'}, ]

        footline.append({'value': total_count,
                         'class': 'total number'})
        footlines.append(footline)

        footline = [{'value': _('Average TAT'),
                     'class': 'total'}, ]

        footline.append({'value': ave_total_duration,
                         'class': 'total number'})
        footlines.append(footline)

        self.report_content = {
            'headings': headings,
            'parms': parms,
            'formats': formats,
            'datalines': datalines,
            'footings': footlines}

        if self.request.get('output_format', '') == 'CSV':
            import csv
            import StringIO
            import datetime

            fieldnames = [
                'Date',
                'Turnaround time (h)',
            ]
            output = StringIO.StringIO()
            dw = csv.DictWriter(output, extrasaction='ignore',
                                fieldnames=fieldnames)
            dw.writerow(dict((fn, fn) for fn in fieldnames))
            for row in datalines:
                dw.writerow({
                    'Date': row[0]['value'],
                    'Turnaround time (h)': row[1]['value'],
                })
            report_data = output.getvalue()
            output.close()
            date = datetime.datetime.now().strftime("%Y%m%d%H%M")
            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'text/csv')
            setheader("Content-Disposition",
                      "attachment;filename=\"analysesperservice_%s.csv\"" % date)
            self.request.RESPONSE.write(report_data)
        else:
            return {'report_title': t(headings['header']),
                    'report_data': self.template()}
