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

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.reports.selection_macros import SelectionMacrosView
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


def percentage(part, whole):
    return


class Report(BrowserView):
    implements(IViewView)
    default_template = ViewPageTemplateFile("templates/productivity.pt")
    template = ViewPageTemplateFile(
        "templates/productivity_samplereceivedvsreported.pt")

    def __init__(self, context, request, report=None):
        super(Report, self).__init__(context, request)
        self.report = report
        self.selection_macros = SelectionMacrosView(self.context, self.request)

    def __call__(self):

        parms = []
        titles = []

        self.contentFilter = dict(portal_type="AnalysisRequest",
                                  is_active=True,
                                  sort_on="getDateReceived")

        val = self.selection_macros.parse_daterange(self.request,
                                                    'getDateReceived',
                                                    _('Date Received'))
        if val:
            self.contentFilter[val['contentFilter'][0]] = val['contentFilter'][1]
            parms.append(val['parms'])
            titles.append(val['titles'])

        # Query the catalog and store results in a dictionary
        ars = api.search(self.contentFilter, CATALOG_ANALYSIS_REQUEST_LISTING)
        if not ars:
            message = _("No samples matched your query")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()

        datalines = {}
        footlines = {}
        total_received_count = 0
        total_published_count = 0
        for ar in ars:
            published = api.get_workflow_status_of(ar) == "published"
            ar = api.get_object(ar)
            datereceived = ar.getDateReceived()
            monthyear = datereceived.strftime("%B") + " " + datereceived.strftime(
                "%Y")
            received = 1
            publishedcnt = published and 1 or 0
            if (monthyear in datalines):
                received = datalines[monthyear]['ReceivedCount'] + 1
                publishedcnt = published and datalines[monthyear][
                                                 'PublishedCount'] + 1 or \
                               datalines[monthyear]['PublishedCount']
            ratio = publishedcnt / received
            dataline = {'MonthYear': monthyear,
                        'ReceivedCount': received,
                        'PublishedCount': publishedcnt,
                        'UnpublishedCount': received - publishedcnt,
                        'Ratio': ratio,
                        'RatioPercentage': '%02d' % (
                        100 * (float(publishedcnt) / float(received))) + '%'}
            datalines[monthyear] = dataline

            total_received_count += 1
            total_published_count = published and total_published_count + 1 or total_published_count

        # Footer total data
        ratio = total_published_count / total_received_count
        footline = {'ReceivedCount': total_received_count,
                    'PublishedCount': total_published_count,
                    'UnpublishedCount': total_received_count - total_published_count,
                    'Ratio': ratio,
                    'RatioPercentage': '%02d' % (100 * (
                    float(total_published_count) / float(
                        total_received_count))) + '%'
        }
        footlines['Total'] = footline

        self.report_data = {
            'parameters': parms,
            'datalines': datalines,
            'footlines': footlines}

        if self.request.get('output_format', '') == 'CSV':
            import csv
            import StringIO
            import datetime

            fieldnames = [
                'MonthYear',
                'ReceivedCount',
                'PublishedCount',
                'RatioPercentage',
            ]
            output = StringIO.StringIO()
            dw = csv.DictWriter(output, extrasaction='ignore',
                                fieldnames=fieldnames)
            dw.writerow(dict((fn, fn) for fn in fieldnames))
            for row in datalines.values():
                dw.writerow(row)
            report_data = output.getvalue()
            output.close()
            date = datetime.datetime.now().strftime("%Y%m%d%H%M")
            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'text/csv')
            setheader("Content-Disposition",
                      "attachment;filename=\"receivedvspublished_%s.csv\"" % date)
            self.request.RESPONSE.write(report_data)
        else:
            return {'report_title': _('Samples received vs. reported'),
                    'report_data': self.template()}
