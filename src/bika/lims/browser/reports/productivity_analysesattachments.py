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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.utils import formatDateParms
from bika.lims.utils import formatDateQuery
from bika.lims.utils import logged_in_client
from bika.lims.utils import t
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class Report(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/report_out.pt")

    def __init__(self, context, request, report=None):
        self.report = report
        BrowserView.__init__(self, context, request)

    def __call__(self):
        # get all the data into datalines

        pc = getToolByName(self.context, 'portal_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        self.report_content = {}
        parms = []
        headings = {}
        headings['header'] = _("Attachments")
        headings['subheader'] = _(
            "The attachments linked to samples and analyses")

        count_all = 0
        query = {'portal_type': 'Attachment'}
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
            else:
                client_title = 'All'
        parms.append(
            {'title': _('Client'),
             'value': client_title,
             'type': 'text'})

        date_query = formatDateQuery(self.context, 'Loaded')
        if date_query:
            query['getDateLoaded'] = date_query
            loaded = formatDateParms(self.context, 'Loaded')
            parms.append(
                {'title': _('Loaded'),
                 'value': loaded,
                 'type': 'text'})

        # and now lets do the actual report lines
        formats = {'columns': 6,
                   'col_heads': [_('Request'),
                                 _('File'),
                                 _('Attachment type'),
                                 _('Content type'),
                                 _('Size'),
                                 _('Loaded'),
                   ],
                   'class': '',
        }

        datalines = []
        attachments = pc(query)
        for a_proxy in attachments:
            attachment = a_proxy.getObject()
            attachment_file = attachment.getAttachmentFile()
            icon = api.get_icon(attachment, False)
            filename = attachment_file.filename
            filesize = attachment_file.get_size()
            filesize = filesize / 1024
            sizeunit = "Kb"
            if filesize > 1024:
                filesize = filesize / 1024
                sizeunit = "Mb"
            dateloaded = attachment.getDateLoaded()
            dataline = []
            dataitem = {'value': attachment.Title()}
            dataline.append(dataitem)
            dataitem = {'value': filename,
                        'img_before': icon}
            dataline.append(dataitem)
            dataitem = {
            'value': attachment.getAttachmentType().Title() if attachment.getAttachmentType() else ''}
            dataline.append(dataitem)
            dataitem = {
            'value': self.context.lookupMime(attachment_file.getContentType())}
            dataline.append(dataitem)
            dataitem = {'value': '%s%s' % (filesize, sizeunit)}
            dataline.append(dataitem)
            dataitem = {'value': self.ulocalized_time(dateloaded)}
            dataline.append(dataitem)

            datalines.append(dataline)

            count_all += 1

        # footer data
        footlines = []
        footline = []
        footitem = {'value': _('Total'),
                    'colspan': 5,
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
            from six import StringIO
            import datetime

            fieldnames = [
                _('Request'),
                _('File'),
                _('Attachment type'),
                _('Content type'),
                _('Size'),
                _('Loaded'),
            ]
            output = StringIO()
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
                      "attachment;filename=\"analysesattachments_%s.csv\"" % date)
            self.request.RESPONSE.write(report_data)
        else:
            return {'report_title': t(headings['header']),
                    'report_data': self.template()}
