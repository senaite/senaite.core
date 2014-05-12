from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.utils import formatDateQuery, formatDateParms, formatDuration, \
    logged_in_client
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

        sc = getToolByName(self.context, 'bika_setup_catalog')
        bc = getToolByName(self.context, 'bika_analysis_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        self.report_content = {}
        parms = []
        headings = {}
        headings['header'] = _("Analysis turnaround times")
        headings['subheader'] = _("The turnaround time of analyses")

        query = {'portal_type': 'Analysis'}
        client_title = None
        if 'ClientUID' in self.request.form:
            client_uid = self.request.form['ClientUID']
            query['getClientUID'] = client_uid
            client = rc.lookupObject(client_uid)
            client_title = client.Title()
        else:
            client = logged_in_client(self.context)
            if client:
                client_title = client.Title()
                query['getClientUID'] = client.UID()
        if client_title:
            parms.append(
                {'title': _('Client'),
                 'value': client_title,
                 'type': 'text'})

        date_query = formatDateQuery(self.context, 'Received')
        if date_query:
            query['created'] = date_query
            received = formatDateParms(self.context, 'Received')
            parms.append(
                {'title': _('Received'),
                 'value': received,
                 'type': 'text'})

        query['review_state'] = 'published'

        workflow = getToolByName(self.context, 'portal_workflow')
        if 'bika_worksheetanalysis_workflow' in self.request.form:
            query['worksheetanalysis_review_state'] = self.request.form[
                'bika_worksheetanalysis_workflow']
            ws_review_state = workflow.getTitleForStateOnType(
                self.request.form['bika_worksheetanalysis_workflow'], 'Analysis')
            parms.append(
                {'title': _('Assigned to worksheet'), 'value': ws_review_state,
                 'type': 'text'})

        # query all the analyses and increment the counts
        count_early = 0
        mins_early = 0
        count_late = 0
        mins_late = 0
        count_undefined = 0
        services = {}

        analyses = bc(query)
        for a in analyses:
            analysis = a.getObject()
            service_uid = analysis.getServiceUID()
            if service_uid not in services:
                services[service_uid] = {'count_early': 0,
                                         'count_late': 0,
                                         'mins_early': 0,
                                         'mins_late': 0,
                                         'count_undefined': 0,
                }
            earliness = analysis.getEarliness()
            if earliness < 0:
                count_late = services[service_uid]['count_late']
                mins_late = services[service_uid]['mins_late']
                count_late += 1
                mins_late -= earliness
                services[service_uid]['count_late'] = count_late
                services[service_uid]['mins_late'] = mins_late
            if earliness > 0:
                count_early = services[service_uid]['count_early']
                mins_early = services[service_uid]['mins_early']
                count_early += 1
                mins_early += earliness
                services[service_uid]['count_early'] = count_early
                services[service_uid]['mins_early'] = mins_early
            if earliness == 0:
                count_undefined = services[service_uid]['count_undefined']
                count_undefined += 1
                services[service_uid]['count_undefined'] = count_undefined

        # calculate averages
        for service_uid in services.keys():
            count_early = services[service_uid]['count_early']
            mins_early = services[service_uid]['mins_early']
            if count_early == 0:
                services[service_uid]['ave_early'] = ''
            else:
                avemins = (mins_early) / count_early
                services[service_uid]['ave_early'] = formatDuration(self.context,
                                                                    avemins)
            count_late = services[service_uid]['count_late']
            mins_late = services[service_uid]['mins_late']
            if count_late == 0:
                services[service_uid]['ave_late'] = ''
            else:
                avemins = mins_late / count_late
                services[service_uid]['ave_late'] = formatDuration(self.context,
                                                                   avemins)

        # and now lets do the actual report lines
        formats = {'columns': 7,
                   'col_heads': [_('Analysis'),
                                 _('Count'),
                                 _('Undefined'),
                                 _('Late'),
                                 _('Average late'),
                                 _('Early'),
                                 _('Average early'),
                   ],
                   'class': '',
        }

        total_count_early = 0
        total_count_late = 0
        total_mins_early = 0
        total_mins_late = 0
        total_count_undefined = 0
        datalines = []

        for cat in sc(portal_type='AnalysisCategory',
                      sort_on='sortable_title'):
            catline = [{'value': cat.Title,
                        'class': 'category_heading',
                        'colspan': 7}, ]
            first_time = True
            cat_count_early = 0
            cat_count_late = 0
            cat_count_undefined = 0
            cat_mins_early = 0
            cat_mins_late = 0
            for service in sc(portal_type="AnalysisService",
                              getCategoryUID=cat.UID,
                              sort_on='sortable_title'):

                dataline = [{'value': service.Title,
                             'class': 'testgreen'}, ]
                if service.UID not in services:
                    continue

                if first_time:
                    datalines.append(catline)
                    first_time = False

                # analyses found
                cat_count_early += services[service.UID]['count_early']
                cat_count_late += services[service.UID]['count_late']
                cat_count_undefined += services[service.UID]['count_undefined']
                cat_mins_early += services[service.UID]['mins_early']
                cat_mins_late += services[service.UID]['mins_late']

                count = services[service.UID]['count_early'] + \
                        services[service.UID]['count_late'] + \
                        services[service.UID]['count_undefined']

                dataline.append({'value': count,
                                 'class': 'number'})
                dataline.append(
                    {'value': services[service.UID]['count_undefined'],
                     'class': 'number'})
                dataline.append({'value': services[service.UID]['count_late'],
                                 'class': 'number'})
                dataline.append({'value': services[service.UID]['ave_late'],
                                 'class': 'number'})
                dataline.append({'value': services[service.UID]['count_early'],
                                 'class': 'number'})
                dataline.append({'value': services[service.UID]['ave_early'],
                                 'class': 'number'})

                datalines.append(dataline)

            # category totals
            dataline = [{'value': '%s - total' % (cat.Title),
                         'class': 'subtotal_label'}, ]

            dataline.append({'value': cat_count_early +
                                      cat_count_late +
                                      cat_count_undefined,
                             'class': 'subtotal_number'})

            dataline.append({'value': cat_count_undefined,
                             'class': 'subtotal_number'})

            dataline.append({'value': cat_count_late,
                             'class': 'subtotal_number'})

            if cat_count_late:
                dataitem = {'value': cat_mins_late / cat_count_late,
                            'class': 'subtotal_number'}
            else:
                dataitem = {'value': 0,
                            'class': 'subtotal_number'}

            dataline.append(dataitem)

            dataline.append({'value': cat_count_early,
                             'class': 'subtotal_number'})

            if cat_count_early:
                dataitem = {'value': cat_mins_early / cat_count_early,
                            'class': 'subtotal_number'}
            else:
                dataitem = {'value': 0,
                            'class': 'subtotal_number'}

            dataline.append(dataitem)

            total_count_early += cat_count_early
            total_count_late += cat_count_late
            total_count_undefined += cat_count_undefined
            total_mins_early += cat_mins_early
            total_mins_late += cat_mins_late

        # footer data
        footlines = []
        footline = []
        footline = [{'value': _('Total'),
                     'class': 'total'}, ]

        footline.append({'value': total_count_early +
                                  total_count_late +
                                  total_count_undefined,
                         'class': 'total number'})

        footline.append({'value': total_count_undefined,
                         'class': 'total number'})

        footline.append({'value': total_count_late,
                         'class': 'total number'})

        if total_count_late:
            ave_mins = total_mins_late / total_count_late
            footline.append({'value': formatDuration(self.context, ave_mins),
                             'class': 'total number'})
        else:
            footline.append({'value': ''})

        footline.append({'value': total_count_early,
                         'class': 'total number'})

        if total_count_early:
            ave_mins = total_mins_early / total_count_early
            footline.append({'value': formatDuration(self.context, ave_mins),
                             'class': 'total number'})
        else:
            footline.append({'value': '',
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
                'Analysis',
                'Count',
                'Undefined',
                'Late',
                'Average late',
                'Early',
                'Average early',
            ]
            output = StringIO.StringIO()
            dw = csv.DictWriter(output, extrasaction='ignore',
                                fieldnames=fieldnames)
            dw.writerow(dict((fn, fn) for fn in fieldnames))
            for row in datalines:
                if len(row) == 1:
                    # category heading thingy
                    continue
                dw.writerow({
                    'Analysis': row[0]['value'],
                    'Count': row[1]['value'],
                    'Undefined': row[2]['value'],
                    'Late': row[3]['value'],
                    'Average late': row[4]['value'],
                    'Early': row[5]['value'],
                    'Average early': row[6]['value'],
                })
            report_data = output.getvalue()
            output.close()
            date = datetime.datetime.now().strftime("%Y%m%d%H%M")
            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'text/csv')
            setheader("Content-Disposition",
                      "attachment;filename=\"analysestats_%s.csv\"" % date)
            self.request.RESPONSE.write(report_data)
        else:
            return {'report_title': t(headings['header']),
                    'report_data': self.template()}
