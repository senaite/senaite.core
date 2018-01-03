# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.utils import formatDateQuery, formatDateParms, logged_in_client
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
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        self.report_content = {}
        parm_lines = {}
        parms = []
        headings = {}
        headings['header'] = _("Analyses per sample type")
        headings['subheader'] = _("Number of analyses requested per sample type")

        count_all = 0
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

        date_query = formatDateQuery(self.context, 'Requested')
        if date_query:
            query['created'] = date_query
            requested = formatDateParms(self.context, 'Requested')
            parms.append(
                {'title': _('Requested'),
                 'value': requested,
                 'type': 'text'})

        workflow = getToolByName(self.context, 'portal_workflow')
        if 'bika_analysis_workflow' in self.request.form:
            query['review_state'] = self.request.form['bika_analysis_workflow']
            review_state = workflow.getTitleForStateOnType(
                self.request.form['bika_analysis_workflow'], 'Analysis')
            parms.append(
                {'title': _('Status'),
                 'value': review_state,
                 'type': 'text'})

        if 'bika_cancellation_workflow' in self.request.form:
            query['cancellation_state'] = self.request.form[
                'bika_cancellation_workflow']
            cancellation_state = workflow.getTitleForStateOnType(
                self.request.form['bika_cancellation_workflow'], 'Analysis')
            parms.append(
                {'title': _('Active'),
                 'value': cancellation_state,
                 'type': 'text'})

        if 'bika_worksheetanalysis_workflow' in self.request.form:
            query['worksheetanalysis_review_state'] = self.request.form[
                'bika_worksheetanalysis_workflow']
            ws_review_state = workflow.getTitleForStateOnType(
                self.request.form['bika_worksheetanalysis_workflow'], 'Analysis')
            parms.append(
                {'title': _('Assigned to worksheet'),
                 'value': ws_review_state,
                 'type': 'text'})

        # and now lets do the actual report lines
        formats = {'columns': 2,
                   'col_heads': [_('Sample type'), _('Number of analyses')],
                   'class': '',
        }

        datalines = []
        for sampletype in sc(portal_type="SampleType",
                             sort_on='sortable_title'):
            query['getSampleTypeUID'] = sampletype.UID
            analyses = bac(query)
            count_analyses = len(analyses)

            dataline = []
            dataitem = {'value': sampletype.Title}
            dataline.append(dataitem)
            dataitem = {'value': count_analyses}

            dataline.append(dataitem)

            datalines.append(dataline)

            count_all += count_analyses

        # footer data
        footlines = []
        footline = []
        footitem = {'value': _('Total'),
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

        if self.request.get('output_format', '') == 'CSV':
            import csv
            import StringIO
            import datetime

            fieldnames = [
                'Sample Type',
                'Analyses',
            ]
            output = StringIO.StringIO()
            dw = csv.DictWriter(output, extrasaction='ignore',
                                fieldnames=fieldnames)
            dw.writerow(dict((fn, fn) for fn in fieldnames))
            for row in datalines:
                dw.writerow({
                    'Sample Type': row[0]['value'],
                    'Analyses': row[1]['value'],
                })
            report_data = output.getvalue()
            output.close()
            date = datetime.datetime.now().strftime("%Y%m%d%H%M")
            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'text/csv')
            setheader("Content-Disposition",
                      "attachment;filename=\"analysespersampletype_%s.csv\"" % date)
            self.request.RESPONSE.write(report_data)
        else:
            return {'report_title': t(headings['header']),
                    'report_data': self.template()}
