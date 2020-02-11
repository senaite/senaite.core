# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import StringIO
import csv
import datetime
from collections import OrderedDict

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.utils import formatDateQuery, formatDateParms, logged_in_client
from bika.lims.utils import t
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class Report(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/report_out.pt")

    def __init__(self, context, request, report=None):
        BrowserView.__init__(self, context, request)
        self.report = report
        self.headings = {
            'header': _("Samples and analyses per client"),
            'subheader': _("Number of Samples and analyses per client"),
        }
        self.formats = {
            'columns': 3,
            'col_heads': [
                _('Client'),
                _('Number of requests'),
                _('Number of analyses')],
            'class': ''
        }

    def __call__(self):
        parms = []

        # Base query
        query = dict(portal_type="Analysis", sort_on='getClientTitle')

        # Filter by client
        self.add_filter_by_client(query, parms)

        # Filter by date
        self.add_filter_by_date(query, parms)

        # Filter analyses by review_state
        self.add_filter_by_review_state(query, parms)

        # Fetch and fill data
        data = OrderedDict()
        analyses = api.search(query, CATALOG_ANALYSIS_LISTING)
        total_num_analyses = len(analyses)
        total_num_ars = 0
        for analysis in analyses:
            client = analysis.getClientTitle
            data_client = data.get(client, {})
            request = analysis.getRequestID
            requests = data_client.get("requests", [])
            if request not in requests:
                requests += [request]
                data_client["requests"] = requests
                total_num_ars += 1
            data_client["analyses"] = data_client.get("analyses", 0) + 1
            data[client] = data_client

        # Generate datalines
        data_lines = list()
        for client, data in data.items():
            ars_count = len(data.get('requests', []))
            ans_count = data.get('analyses', 0)
            data_lines.append([{"value": client},
                               {"value": ars_count},
                               {"value": ans_count}])

        if self.request.get('output_format', '') == 'CSV':
            return self.generate_csv(data_lines)

        self.report_content = {
            'headings': self.headings,
            'parms': parms,
            'formats': self.formats,
            'datalines': data_lines,
            'footings': [
                [{'value': _('Total'), 'class': 'total_label'},
                 {'value': total_num_ars},
                 {'value': total_num_analyses},],]
        }

        return {'report_title': t(self.headings['header']),
                'report_data': self.template()}

    def add_filter_by_client(self, query, out_params):
        """Applies the filter by client to the search query
        """
        current_client = logged_in_client(self.context)
        if current_client:
            query['getClientUID'] = api.get_uid(current_client)
        elif self.request.form.get("ClientUID", ""):
            query['getClientUID'] = self.request.form['ClientUID']
            client = api.get_object_by_uid(query['getClientUID'])
            out_params.append({'title': _('Client'),
                               'value': client.Title(),
                               'type': 'text'})

    def add_filter_by_date(self, query, out_params):
        """Applies the filter by Requested date to the search query
        """
        date_query = formatDateQuery(self.context, 'Requested')
        if date_query:
            query['created'] = date_query
            requested = formatDateParms(self.context, 'Requested')
            out_params.append({'title': _('Requested'),
                               'value': requested,
                               'type': 'text'})

    def add_filter_by_review_state(self, query, out_params):
        """Applies the filter by review_state to the search query
        """
        self.add_filter_by_wf_state(query=query, out_params=out_params,
                                    wf_id="bika_analysis_workflow",
                                    index="review_state",
                                    title=_("Status"))

    def add_filter_by_wf_state(self, query, out_params, wf_id, index,
                               title):
        if not self.request.form.get(wf_id, ""):
            return
        query[index] = self.request.form[wf_id]
        workflow = api.get_tool("portal_workflow")
        state = workflow.getTitleForStateOnType(query[index], 'Analysis')
        out_params.append({'title': title, 'value': state, 'type': 'text'})

    def generate_csv(self, data_lines):
        """Generates and writes a CSV to request's reposonse
        """
        fieldnames = [
            'Client',
            'Samples',
            'Analyses',
        ]
        output = StringIO.StringIO()
        dw = csv.DictWriter(output, extrasaction='ignore',
                            fieldnames=fieldnames)
        dw.writerow(dict((fn, fn) for fn in fieldnames))
        for row in data_lines:
            dw.writerow({
                'Client': row[0]['value'],
                'Samples': row[1]['value'],
                'Analyses': row[2]['value'],
            })
        report_data = output.getvalue()
        output.close()

        date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        setheader = self.request.RESPONSE.setHeader
        setheader('Content-Type', 'text/csv')
        setheader("Content-Disposition",
                  "attachment;filename=\"analysesperclient_%s.csv\"" % date)
        self.request.RESPONSE.write(report_data)
