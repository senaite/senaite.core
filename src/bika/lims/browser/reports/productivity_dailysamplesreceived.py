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
            message = _("No Samples matched your query")
            self.context.plone_utils.addPortalMessage(message, "error")
            return self.default_template()

        datalines = []
        analyses_count = 0
        for ar in ars:
            ar = api.get_object(ar)
            # For each sample, retrieve the analyses and generate
            # a data line for each one
            for analysis in ar.getAnalyses():
                analysis = analysis.getObject()
                ds = ar.getDateSampled()
                sd = ar.getSamplingDate()
                dataline = {'AnalysisKeyword': analysis.getKeyword(),
                            'AnalysisTitle': analysis.Title(),
                            'SampleID': ar.getId(),
                            'SampleType': ar.getSampleType().Title(),
                            'DateReceived': self.ulocalized_time(
                                ar.getDateReceived(), long_format=1),
                            'DateSampled': self.ulocalized_time(
                                ds, long_format=1),
                            }
                if self.context.bika_setup.getSamplingWorkflowEnabled():
                    dataline['SamplingDate']= self.ulocalized_time(
                                              sd, long_format=1)
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
                'DateSampled',
                'DateReceived',
                'AnalysisTitle',
                'AnalysisKeyword',
            ]
            if self.context.bika_setup.getSamplingWorkflowEnabled():
                fieldnames.append('SamplingDate')
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
