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

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.utils import formatDateQuery, formatDateParms
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
            'header': _("Analysis turnaround times over time"),
            'subheader': _("The turnaround time of analyses plotted over time")
        }
        self.formats = {
            'columns': 2,
            'col_heads': [
                _('Date'),
                 _('Turnaround time (h)')],
            'class': ''
        }

    def __call__(self):
        parms = []
        query = dict(portal_type="Analysis", sort_on="getDateReceived",
                     sort_order="ascending")

        # Filter by Service UID
        self.add_filter_by_service(query=query, out_params=parms)

        # Filter by Analyst
        self.add_filter_by_analyst(query=query, out_params=parms)

        # Filter by date range
        self.add_filter_by_date_range(query=query, out_params=parms)

        # Period
        period = self.request.form.get("Period", "Day")
        parms.append(
            {"title": _("Period"),
             "value": period,
             "type": "text"}
        )

        # Fetch the data
        data_lines = []
        prev_date_key = None
        count = 0
        duration = 0
        total_count = 0
        total_duration = 0
        analyses = api.search(query, CATALOG_ANALYSIS_LISTING)
        for analysis in analyses:
            analysis = api.get_object(analysis)
            date_key = self.get_period_key(analysis.getDateReceived(),
                                           self.date_format_short)
            if date_key and date_key != prev_date_key:
                if prev_date_key:
                    # Calculate averages
                    data_lines.append(
                        [{"value": prev_date_key, 'class': ''},
                         {"value": api.to_dhm_format(minutes=(duration//count)),
                          "class": "number"}]
                    )
                count = 0
                duration = 0

            analysis_duration = analysis.getDuration()
            count += 1
            total_count += 1
            duration += analysis_duration
            total_duration += analysis_duration
            prev_date_key = date_key

        if prev_date_key:
            # Calculate averages
            data_lines.append(
                [{"value": prev_date_key, 'class': ''},
                 {"value": api.to_dhm_format(minutes=(duration//count)),
                  "class": "number"}]
            )

        # Totals
        total_duration = total_count and total_duration / total_count or 0
        total_duration = api.to_dhm_format(minutes=total_duration)

        if self.request.get("output_format", "") == "CSV":
            return self.generate_csv(data_lines)

        self.report_content = {
            'headings': self.headings,
            'parms': parms,
            'formats': self.formats,
            'datalines': data_lines,
            'footings': [
                [{'value': _('Total data points'), 'class': 'total'},
                 {'value': total_count, 'class': 'total number'}],

                [{'value': _('Average TAT'), 'class': 'total'},
                 {'value': total_duration, 'class': 'total number'}]
        ]}
        return {'report_title': t(self.headings['header']),
                'report_data': self.template()}

    def add_filter_by_service(self, query, out_params):
        if not self.request.form.get("ServiceUID", ""):
            return
        query["getServiceUID"] = self.request.form["ServiceUID"]
        service = api.get_object_by_uid(query["getServiceUID"])
        out_params.append({
            "title": _("Analysis Service"),
            "value": service.Title(),
            "type": "text"})

    def add_filter_by_analyst(self, query, out_params):
        if not self.request.form.get("Analyst", ""):
            return
        query["getAnalyst"] = self.request.form["Analyst"]
        out_params.append({
            "title": _("Analyst"),
            "value": self.user_fullname(query["getAnalyst"]),
            "type": "text"})

    def add_filter_by_instrument(self, query, out_params):
        if not self.request.form.get("getInstrumentUID", ""):
            return
        query["getInstrumentUID"] = self.request.form["getInstrumentUID"]
        instrument = api.get_object_by_uid(query["getInstrumentUID"])
        out_params.append({
            "title": _("Instrument"),
            "value": instrument.Title(),
            "type": "text"})

    def add_filter_by_date_range(self, query, out_params):
        date_query = formatDateQuery(self.context, "tats_DateReceived")
        if not date_query:
            return
        query["getDateReceived"] = date_query
        out_params.append(
            {"title": _("Received"),
             "value": formatDateParms(self.context, "Tats_DateReceived"),
             "type": "text"}
        )

    def get_period_key(self, date_time, date_format):
        period = self.request.form.get("Period", "Day")
        if period == "Day":
            return date_time.strftime('%d %b %Y')
        elif period == "Week":
            day_of_week = date_time.strftime("%w")
            first_day = date_time - (int(day_of_week) - 1)
            # Sunday = 0
            if not day_of_week:
                first_day = date_time - 6
            return first_day.strftime(date_format)
        elif period == "Month":
            return date_time.strftime("%b %Y")
        return "unknown"

    def generate_csv(self, data_lines):
        fieldnames = [
            'Date',
            'Turnaround time (h)',
        ]
        output = StringIO.StringIO()
        dw = csv.DictWriter(output, extrasaction='ignore',
                            fieldnames=fieldnames)
        dw.writerow(dict((fn, fn) for fn in fieldnames))
        for row in data_lines:
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
