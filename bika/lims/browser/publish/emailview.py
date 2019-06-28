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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import inspect
import mimetypes
import socket
from collections import OrderedDict
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from smtplib import SMTPException
from string import Template

import transaction
from bika.lims import _
from bika.lims import api
from bika.lims import logger
from bika.lims.decorators import returns_json
from bika.lims.utils import to_utf8
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import POSKeyError
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

EMAIL_MAX_SIZE = 15


class EmailView(BrowserView):
    """Email Attachments View
    """
    implements(IPublishTraverse)

    template = ViewPageTemplateFile("templates/email.pt")
    email_template = ViewPageTemplateFile("templates/email_template.pt")

    def __init__(self, context, request):
        super(EmailView, self).__init__(context, request)
        # disable Plone's editable border
        request.set("disable_border", True)
        # remember context/request
        self.context = context
        self.request = request
        self.url = self.context.absolute_url()
        # the URL to redirect on cancel or after send
        self.exit_url = "{}/{}".format(self.url, "reports_listing")
        # we need to transform the title to unicode, so that we can use it for
        self.client_name = safe_unicode(self.context.Title())
        self.email_body = self.context.translate(_(self.email_template(self)))
        # string interpolation later
        # N.B. We need to translate the raw string before interpolation
        subject = self.context.translate(_("Analysis Results for {}"))
        self.email_subject = subject.format(self.client_name)
        self.allow_send = True
        self.traverse_subpath = []

    def __call__(self):
        # handle subpath request
        if len(self.traverse_subpath) > 0:
            return self.handle_ajax_request()
        # handle standard request
        return self.handle_http_request()

    def publishTraverse(self, request, name):
        """Called before __call__ for each path name
        """
        self.traverse_subpath.append(name)
        return self

    def fail(self, message, status=500, **kw):
        """Set a JSON error object and a status to the response
        """
        self.request.response.setStatus(status)
        result = {"success": False, "errors": message, "status": status}
        result.update(kw)
        return result

    @returns_json
    def handle_ajax_request(self):
        """Handle requests ajax routes
        """
        # check if the method exists
        func_arg = self.traverse_subpath[0]
        func_name = "ajax_{}".format(func_arg)
        func = getattr(self, func_name, None)

        if func is None:
            return self.fail("Invalid function", status=400)

        # Additional provided path segments after the function name are handled
        # as positional arguments
        args = self.traverse_subpath[1:]

        # check mandatory arguments
        func_sig = inspect.getargspec(func)
        # positional arguments after `self` argument
        required_args = func_sig.args[1:]

        if len(args) < len(required_args):
            return self.fail("Wrong signature, please use '{}/{}'"
                             .format(func_arg, "/".join(required_args)), 400)
        return func(*args)

    def handle_http_request(self):
        request = self.request
        form = request.form

        submitted = form.get("submitted", False)
        send = form.get("send", False)
        cancel = form.get("cancel", False)

        if submitted and send:
            logger.info("*** SENDING EMAIL ***")

            # Parse used defined values from the request form
            recipients = form.get("recipients", [])
            responsibles = form.get("responsibles", [])
            subject = form.get("subject")
            body = form.get("body")
            reports = self.get_reports()

            # Merge recipiens and responsibles
            recipients = set(recipients + responsibles)

            # sanity checks
            if not recipients:
                message = _("No email recipients selected")
                self.add_status_message(message, "error")
            if not subject:
                message = _("Please add an email subject")
                self.add_status_message(message, "error")
            if not body:
                message = _("Please add an email text")
                self.add_status_message(message, "error")
            if not reports:
                message = _("No attachments")
                self.add_status_message(message, "error")

            success = False
            if all([recipients, subject, body, reports]):
                attachments = []

                # report pdfs
                for report in reports:
                    pdf = self.get_pdf(report)
                    if pdf is None:
                        logger.error("Skipping empty PDF for report {}"
                                     .format(report.getId()))
                        continue
                    ar = report.getAnalysisRequest()
                    filename = "{}.pdf".format(ar.getId())
                    filedata = pdf.data
                    attachments.append(
                        self.to_email_attachment(filename, filedata))

                # additional attachments
                for attachment in self.get_attachments():
                    af = attachment.getAttachmentFile()
                    filedata = af.data
                    filename = af.filename
                    attachments.append(
                        self.to_email_attachment(filename, filedata))

                success = self.send_email(
                    recipients, subject, body, attachments=attachments)

                # make a savepoint to avoid multiple email send
                # http://www.zodb.org/en/latest/reference/transaction.html
                transaction.savepoint(optimistic=True)

            if success:
                # selected name, email pairs which received the email
                pairs = map(self.parse_email, recipients)
                send_to_names = map(lambda p: p[0], pairs)

                # set recipients to the reports
                for report in reports:
                    ar = report.getAnalysisRequest()
                    # publish the AR
                    self.publish(ar)

                    # Publish all linked ARs of this report
                    # N.B. `ContainedAnalysisRequests` is an extended field
                    field = report.getField("ContainedAnalysisRequests")
                    contained_ars = field.get(report) or []
                    for obj in contained_ars:
                        # skip the primary AR
                        if obj == ar:
                            continue
                        self.publish(obj)

                    # add new recipients to the AR Report
                    new_recipients = filter(
                        lambda r: r.get("Fullname") in send_to_names,
                        self.get_recipients(ar))
                    self.set_report_recipients(report, new_recipients)

                message = _(u"Message sent to {}"
                            .format(", ".join(send_to_names)))
                self.add_status_message(message, "info")
                return request.response.redirect(self.exit_url)
            else:
                message = _("Failed to send Email(s)")
                self.add_status_message(message, "error")

        if submitted and cancel:
            logger.info("*** EMAIL CANCELLED ***")
            message = _("Email cancelled")
            self.add_status_message(message, "info")
            return request.response.redirect(self.exit_url)

        # get the selected ARReport objects
        reports = self.get_reports()
        attachments = self.get_attachments()

        # calculate the total size of all PDFs
        self.total_size = self.get_total_size(reports, attachments)
        if self.total_size > self.max_email_size:
            # don't allow to send oversized emails
            self.allow_send = False
            message = _("Total size of email exceeded {:.1f} MB ({:.2f} MB)"
                        .format(self.max_email_size / 1024,
                                self.total_size / 1024))
            self.add_status_message(message, "error")

        # prepare the data for the template
        self.reports = map(self.get_report_data, reports)
        self.recipients = self.get_recipients_data(reports)
        self.responsibles = self.get_responsibles_data(reports)

        # inform the user about invalid recipients
        if not all(map(lambda r: r.get("valid"), self.recipients)):
            message = _(
                "Not all contacts are equal for the selected Reports. "
                "Please manually select recipients for this email.")
            self.add_status_message(message, "warning")

        return self.template()

    def set_report_recipients(self, report, recipients):
        """Set recipients to the reports w/o overwriting the old ones

        :param reports: list of ARReports
        :param recipients: list of name,email strings
        """
        to_set = report.getRecipients()
        for recipient in recipients:
            if recipient not in to_set:
                to_set.append(recipient)
        report.setRecipients(to_set)

    def publish(self, ar):
        """Set status to prepublished/published/republished
        """
        # Manually update the view on the database to avoid conflict errors
        ar.getClient()._p_jar.sync()

        wf = api.get_tool("portal_workflow")
        status = wf.getInfoFor(ar, "review_state")
        transitions = {"verified": "publish",
                       "published": "republish"}
        transition = transitions.get(status, "prepublish")
        logger.info("AR Transition: {} -> {}".format(status, transition))
        try:
            wf.doActionFor(ar, transition)
            # Commit the changes
            transaction.commit()
            return True
        except WorkflowException as e:
            logger.debug(e)
            return False

    def parse_email(self, email):
        """parse an email to an unicode name, email tuple
        """
        splitted = safe_unicode(email).rsplit(",", 1)
        if len(splitted) == 1:
            return (False, splitted[0])
        elif len(splitted) == 2:
            return (splitted[0], splitted[1])
        else:
            raise ValueError("Could not parse email '{}'".format(email))

    def to_email_attachment(self, filename, filedata, **kw):
        """Create a new MIME Attachment

        The Content-Type: header is build from the maintype and subtype of the
        guessed filename mimetype. Additional parameters for this header are
        taken from the keyword arguments.
        """
        maintype = "application"
        subtype = "octet-stream"

        mime_type = mimetypes.guess_type(filename)[0]
        if mime_type is not None:
            maintype, subtype = mime_type.split("/")

        attachment = MIMEBase(maintype, subtype, **kw)
        attachment.set_payload(filedata)
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition",
                              "attachment; filename=%s" % filename)
        return attachment

    def send_email(self, recipients, subject, body, attachments=None):
        """Prepare and send email to the recipients

        :param recipients: a list of email or name,email strings
        :param subject: the email subject
        :param body: the email body
        :param attachments: list of email attachments
        :returns: True if all emails were sent, else false
        """

        recipient_pairs = map(self.parse_email, recipients)
        template_context = {
            "recipients": "\n".join(
                map(lambda p: formataddr(p), recipient_pairs))
        }

        body_template = Template(safe_unicode(body)).safe_substitute(
            **template_context)

        _preamble = "This is a multi-part message in MIME format.\n"
        _from = formataddr((self.email_from_name, self.email_from_address))
        _subject = Header(s=safe_unicode(subject), charset="utf8")
        _body = MIMEText(body_template, _subtype="plain", _charset="utf8")

        # Create the enclosing message
        mime_msg = MIMEMultipart()
        mime_msg.preamble = _preamble
        mime_msg["Subject"] = _subject
        mime_msg["From"] = _from
        mime_msg.attach(_body)

        # Attach attachments
        for attachment in attachments:
            mime_msg.attach(attachment)

        success = []
        # Send one email per recipient
        for pair in recipient_pairs:
            # N.B.: Headers are added additive, so we need to remove any
            #       existing "To" headers
            # No KeyError is raised if the key does not exist.
            # https://docs.python.org/2/library/email.message.html#email.message.Message.__delitem__
            del mime_msg["To"]

            # N.B. we use just the email here to prevent this Postfix Error:
            # Recipient address rejected: User unknown in local recipient table
            mime_msg["To"] = pair[1]
            msg_string = mime_msg.as_string()
            sent = self.send(msg_string)
            if not sent:
                logger.error("Could not send email to {}".format(pair))
            success.append(sent)

        if not all(success):
            return False
        return True

    def send(self, msg_string, immediate=True):
        """Send the email via the MailHost tool
        """
        try:
            mailhost = api.get_tool("MailHost")
            mailhost.send(msg_string, immediate=immediate)
        except SMTPException as e:
            logger.error(e)
            return False
        except socket.error as e:
            logger.error(e)
            return False
        return True

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def get_report_data(self, report):
        """Report data to be used in the template
        """
        ar = report.getAnalysisRequest()
        attachments = map(self.get_attachment_data, ar.getAttachment())
        pdf = self.get_pdf(report)
        filesize = "{} Kb".format(self.get_filesize(pdf))
        filename = "{}.pdf".format(ar.getId())

        return {
            "ar": ar,
            "attachments": attachments,
            "pdf": pdf,
            "obj": report,
            "uid": api.get_uid(report),
            "filesize": filesize,
            "filename": filename,
        }

    def get_attachment_data(self, attachment):
        """Attachments data
        """
        f = attachment.getAttachmentFile()
        attachment_type = attachment.getAttachmentType()
        attachment_keys = attachment.getAttachmentKeys()
        filename = f.filename
        filesize = self.get_filesize(f)
        mimetype = f.getContentType()
        report_option = attachment.getReportOption()

        return {
            "obj": attachment,
            "attachment_type": attachment_type,
            "attachment_keys": attachment_keys,
            "file": f,
            "uid": api.get_uid(attachment),
            "filesize": filesize,
            "filename": filename,
            "mimetype": mimetype,
            "report_option": report_option,
        }

    def get_recipients_data(self, reports):
        """Recipients data to be used in the template
        """
        if not reports:
            return []

        recipients = []
        recipient_names = []

        for num, report in enumerate(reports):
            # get the linked AR of this ARReport
            ar = report.getAnalysisRequest()
            # recipient names of this report
            report_recipient_names = []
            for recipient in self.get_recipients(ar):
                name = recipient.get("Fullname")
                email = recipient.get("EmailAddress")
                record = {
                    "name": name,
                    "email": email,
                    "valid": True,
                }
                if record not in recipients:
                    recipients.append(record)
                # remember the name of the recipient for this report
                report_recipient_names.append(name)
            recipient_names.append(report_recipient_names)

        # recipient names, which all of the reports have in common
        common_names = set(recipient_names[0]).intersection(*recipient_names)
        # mark recipients not in common
        for recipient in recipients:
            if recipient.get("name") not in common_names:
                recipient["valid"] = False
        return recipients

    def get_responsibles_data(self, reports):
        """Responsibles data to be used in the template
        """
        if not reports:
            return []

        recipients = []
        recipient_names = []

        for num, report in enumerate(reports):
            # get the linked AR of this ARReport
            ar = report.getAnalysisRequest()

            # recipient names of this report
            report_recipient_names = []
            responsibles = ar.getResponsible()
            for manager_id in responsibles.get("ids", []):
                responsible = responsibles["dict"][manager_id]
                name = responsible.get("name")
                email = responsible.get("email")
                record = {
                    "name": name,
                    "email": email,
                    "valid": True,
                }
                if record not in recipients:
                    recipients.append(record)
                # remember the name of the recipient for this report
                report_recipient_names.append(name)
            recipient_names.append(report_recipient_names)

        # recipient names, which all of the reports have in common
        common_names = set(recipient_names[0]).intersection(*recipient_names)
        # mark recipients not in common
        for recipient in recipients:
            if recipient.get("name") not in common_names:
                recipient["valid"] = False

        return recipients

    @property
    def portal(self):
        return api.get_portal()

    @property
    def laboratory(self):
        return api.get_setup().laboratory

    @property
    def email_from_address(self):
        """Portal email
        """
        lab_email = self.laboratory.getEmailAddress()
        portal_email = self.portal.email_from_address
        return lab_email or portal_email

    @property
    def email_from_name(self):
        """Portal email name
        """
        lab_from_name = self.laboratory.getName()
        portal_from_name = self.portal.email_from_name
        return lab_from_name or portal_from_name

    def get_total_size(self, *files):
        """Calculate the total size of the given files
        """

        # Recursive unpack an eventual list of lists
        def iterate(item):
            if isinstance(item, (list, tuple)):
                for i in item:
                    for ii in iterate(i):
                        yield ii
            else:
                yield item

        # Calculate the total size of the given objects starting with an
        # initial size of 0
        return reduce(lambda x, y: x + y,
                      map(self.get_filesize, iterate(files)), 0)

    @property
    def max_email_size(self):
        """Return the max. allowed email size in KB
        """
        # TODO: Refactor to customizable setup option
        max_size = EMAIL_MAX_SIZE
        if max_size < 0:
            return 0.0
        return max_size * 1024

    def get_reports(self):
        """Return the objects from the UIDs given in the request
        """
        # Create a mapping of source ARs for copy
        uids = self.request.form.get("uids", [])
        # handle 'uids' GET parameter coming from a redirect
        if isinstance(uids, basestring):
            uids = uids.split(",")
        uids = filter(api.is_uid, uids)
        unique_uids = OrderedDict().fromkeys(uids).keys()
        return map(self.get_object_by_uid, unique_uids)

    def get_attachments(self):
        """Return the objects from the UIDs given in the request
        """
        # Create a mapping of source ARs for copy
        uids = self.request.form.get("attachment_uids", [])
        return map(self.get_object_by_uid, uids)

    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID #{} !!")
        return obj

    def get_filesize(self, f):
        """Return the filesize of the PDF as a float
        """
        try:
            filesize = float(f.get_size())
            return float("%.2f" % (filesize / 1024))
        except (POSKeyError, TypeError, AttributeError):
            return 0.0

    def get_pdf(self, obj):
        """Get the report PDF
        """
        try:
            return obj.getPdf()
        except (POSKeyError, TypeError):
            return None

    def get_recipients(self, ar):
        """Return the AR recipients in the same format like the AR Report
        expects in the records field `Recipients`
        """
        plone_utils = api.get_tool("plone_utils")

        def is_email(email):
            if not plone_utils.validateSingleEmailAddress(email):
                return False
            return True

        def recipient_from_contact(contact):
            if not contact:
                return None
            email = contact.getEmailAddress()
            return {
                "UID": api.get_uid(contact),
                "Username": contact.getUsername(),
                "Fullname": to_utf8(contact.Title()),
                "EmailAddress": email,
            }

        def recipient_from_email(email):
            if not is_email(email):
                return None
            return {
                "UID": "",
                "Username": "",
                "Fullname": email,
                "EmailAddress": email,
            }

        # Primary Contacts
        to = filter(None, [recipient_from_contact(ar.getContact())])
        # CC Contacts
        cc = filter(None, map(recipient_from_contact, ar.getCCContact()))
        # CC Emails
        cc_emails = map(lambda x: x.strip(), ar.getCCEmails().split(","))
        cc_emails = filter(None, map(recipient_from_email, cc_emails))

        return to + cc + cc_emails

    def ajax_recalculate_size(self):
        """Recalculate the total size of the selected attachments
        """
        reports = self.get_reports()
        attachments = self.get_attachments()
        total_size = self.get_total_size(reports, attachments)

        return {
            "files": len(reports) + len(attachments),
            "size": "%.2f" % total_size,
            "limit": self.max_email_size,
            "limit_exceeded": total_size > self.max_email_size,
        }
