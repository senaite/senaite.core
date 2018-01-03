# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTPRecipientsRefused
from smtplib import SMTPServerDisconnected

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.utils import createPdf, encode_header
from bika.lims.utils import t
from zope.component import getAdapters


class ResultOutOfRangeIcons(object):
    """An icon provider for Analyses: Result field out-of-range alerts
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, specification=None, **kwargs):
        translate = self.context.translate
        path = '++resource++bika.lims.images'
        alerts = {}
        # We look for IResultOutOfRange adapters for this object
        for name, adapter in getAdapters((self.context, ), IResultOutOfRange):
            ret = adapter(result)
            if not ret:
                continue
            spec = ret["spec_values"]
            if spec:
                rngstr = " ({0} {1}, {2}, {3})".format(
                    t(_("min")), str(spec['min']),
                    t(_("max")), str(spec['max']))
            else:
                rngstr = ""
            if ret["out_of_range"]:
                if ret["acceptable"]:
                    message = "{0}{1}".format(
                        t(_('Result in shoulder range')),
                        rngstr)
                    icon = path + '/warning.png'
                else:
                    message = "{0}{1}".format(
                        t(_('Result out of range')),
                        rngstr)
                    icon = path + '/exclamation.png'
                alerts[self.context.UID()] = [
                    {
                        'icon': icon,
                        'msg': message,
                        'field': 'Result',
                    },
                ]
            break
        return alerts


class ResultOutOfRange(object):
    """An icon provider for Analyses: Result field out-of-range alerts
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, specification=None):
        workflow = getToolByName(self.context, 'portal_workflow')
        # We don't care about retracted objects
        astate = workflow.getInfoFor(self.context, 'review_state')
        if astate == 'retracted':
            return None
        # We don't care about analyses with no results
        result = str(result) if result is not None else self.context.getResult()
        try:
            result = float(str(result))
        except ValueError:
            return None
        service_uid = self.context.getServiceUID()
        specification = self.context.aq_parent.getResultsRangeDict()
        # Analysis without specification values. Assume in range
        if service_uid not in specification:
            return None

        outofrange, acceptable, o_spec = \
            self.isOutOfRange(result, specification[service_uid])
        return {
            'out_of_range': outofrange,
            'acceptable': acceptable,
            'spec_values': o_spec
        }


    def isOutOfRange(self, result=None, specification=None):
        try:
            spec_min = float(specification['min'])
        except ValueError:
            spec_min = None
        try:
            spec_max = float(specification['max'])
        except ValueError:
            spec_max = None
        if spec_min == 0 and spec_max == 0 and result != 0:
            # Value has to be zero
            outofrange, acceptable, o_spec = True, False, specification
        elif not spec_min and not spec_max:
            # No min and max values defined
            outofrange, acceptable, o_spec = False, None, None
        elif spec_min and spec_max and spec_min <= result <= spec_max:
            # min and max values defined
            outofrange, acceptable, o_spec = False, None, None
        elif spec_min and not spec_max and spec_min <= result:
            # max value not defined
            outofrange, acceptable, o_spec = False, None, None
        elif not spec_min and spec_max and spec_max >= result:
            # min value not defined
            outofrange, acceptable, o_spec = False, None, None
        else:
            outofrange, acceptable, o_spec = True, False, specification

        if not outofrange:
            """ check if in 'shoulder' error range - out of range,
                but in acceptable error """
            error = 0
            try:
                error = float(specification.get('error', '0'))
            except:
                error = 0
                pass
            error_amount = (result / 100) * error
            error_min = result - error_amount
            error_max = result + error_amount
            if (spec_min and result < spec_min <= error_max) \
                    or (spec_max and result > spec_max >= error_min):
                outofrange, acceptable, o_spec = True, True, specification
        return outofrange, acceptable, o_spec


class AnalysesRetractedListReport(BrowserView):
    """ Generates a report with a list of analyses retracted
    """
    template = ViewPageTemplateFile("templates/analyses_retractedlist.pt")

    def __init__(self, context, request, portal_url, title='Retracted analyses',
                 analyses=()):
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

                ws = an.getBackReferences("WorksheetAnalysis")
                if ws and len(ws) > 0:
                    wss = ws[0]
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


