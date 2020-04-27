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

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTPRecipientsRefused
from smtplib import SMTPServerDisconnected

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.utils import createPdf, encode_header


class AnalysesRetractedListReport(BrowserView):
    """ Generates a report with a list of analyses retracted
    """
    template = ViewPageTemplateFile("templates/analyses_retractedlist.pt")

    def __init__(self, context, request, portal_url,
                 title='Retracted analyses', analyses=()):
        super(AnalysesRetractedListReport, self).__init__(context, request)
        self.analyses = analyses
        self.title = title
        self._data = None
        self.request = request
        self.context = context
        self.portal_url = portal_url

    def getData(self):
        if not self._data:
            self._data = []
            for an in self.analyses:
                item = {'ar': '',
                        'ar_url': '',
                        'ar_id': '',
                        'ar_html': '',
                        'ws': '',
                        'ws_url': '',
                        'ws_id': '',
                        'ws_html': '',
                        'an': an,
                        'an_id': an.id,
                        'an_title': an.Title()}

                if IRequestAnalysis.providedBy(an):
                    ar = an.getRequest()
                    item['ar'] = ar
                    item['ar_url'] = ar.absolute_url()
                    item['ar_id'] = ar.getId()
                    item['ar_html'] = \
                        "<a href='%s'>%s</a>" % (item['ar_url'], item['ar_id'])

                ws = an.getWorksheet()
                if ws:
                    item['ws'] = ws
                    item['ws_url'] = ws.absolute_url()
                    item['ws_id'] = ws.id
                    item['ws_html'] = "<a href='%s'>%s</a>" \
                                      % (item['ws_url'], item['ws_id'])
                self._data.append(item)
        return self._data

    def toPdf(self):
        html = safe_unicode(self.template()).encode('utf-8')
        pdf_data = createPdf(html)
        return pdf_data

    def sendEmail(self):
        added = []
        to = ''
        for analysis in self.analyses:
            department = analysis.getDepartment()
            if department is None:
                continue
            department_id = department.UID()
            if department_id in added:
                continue
            added.append(department_id)
            manager = department.getManager()
            if manager is None:
                continue
            manager_id = manager.UID()
            if manager_id not in added and manager.getEmailAddress():
                added.append(manager_id)
                name = safe_unicode(manager.getFullname()).encode('utf-8')
                email = safe_unicode(manager.getEmailAddress()).encode('utf-8')
                to = '%s, %s' % (to, formataddr((encode_header(name), email)))
        html = safe_unicode(self.template()).encode('utf-8')
        lab = self.context.bika_setup.laboratory
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = self.title
        mime_msg['From'] = formataddr(
            (encode_header(lab.getName()),
             lab.getEmailAddress()))
        mime_msg['To'] = to
        mime_msg.preamble = 'This is a multi-part MIME message.'
        msg_txt = MIMEText(html, _subtype='html')
        mime_msg.attach(msg_txt)
        # Send the email
        try:
            host = getToolByName(self.context, 'MailHost')
            host.send(mime_msg.as_string(), immediate=True)
        except SMTPServerDisconnected as msg:
            raise SMTPServerDisconnected(msg)
        except SMTPRecipientsRefused as msg:
            raise WorkflowException(str(msg))
