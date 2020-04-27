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

import inspect
import itertools
import re
from collections import OrderedDict
from string import Template

import transaction
from bika.lims import _
from bika.lims import api
from bika.lims import logger
from bika.lims.api import mail as mailapi
from bika.lims.api.security import get_user
from bika.lims.api.security import get_user_id
from bika.lims.api.snapshot import take_snapshot
from bika.lims.decorators import returns_json
from bika.lims.utils import to_utf8
from DateTime import DateTime
from plone.memoize import view
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import POSKeyError
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

DEFAULT_MAX_EMAIL_SIZE = 15


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
        # list of requested subpaths
        self.traverse_subpath = []
        # toggle to allow email sending
        self.allow_send = True

    def __call__(self):
        # dispatch subpath request to `ajax_` methods
        if len(self.traverse_subpath) > 0:
            return self.handle_ajax_request()

        # handle standard request
        form = self.request.form
        send = form.get("send", False) and True or False
        cancel = form.get("cancel", False) and True or False

        if send and self.validate_email_form():
            logger.info("*** PUBLISH SAMPLES & SEND REPORTS ***")
            # 1. Publish all samples
            self.publish_samples()
            # 2. Notify all recipients
            self.form_action_send()

        elif cancel:
            logger.info("*** CANCEL EMAIL PUBLICATION ***")
            self.form_action_cancel()

        else:
            logger.info("*** RENDER EMAIL FORM ***")
            # validate email size
            self.validate_email_size()
            # validate email recipients
            self.validate_email_recipients()

        return self.template()

    def publishTraverse(self, request, name):
        """Called before __call__ for each path name

        Appends the path to the additional requested path after the view name
        to the internal `traverse_subpath` list
        """
        self.traverse_subpath.append(name)
        return self

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

    def form_action_send(self):
        """Send form handler
        """
        # send email to the selected recipients and responsibles
        success = self.send_email(self.email_recipients_and_responsibles,
                                  self.email_subject,
                                  self.email_body,
                                  attachments=self.email_attachments)

        if success:
            # write email sendlog log to keep track of the email submission
            self.write_sendlog()
            message = _(u"Message sent to {}".format(
                ", ".join(self.email_recipients_and_responsibles)))
            self.add_status_message(message, "info")
        else:
            message = _("Failed to send Email(s)")
            self.add_status_message(message, "error")

        self.request.response.redirect(self.exit_url)

    def form_action_cancel(self):
        """Cancel form handler
        """
        self.add_status_message(_("Email cancelled"), "info")
        self.request.response.redirect(self.exit_url)

    def validate_email_form(self):
        """Validate if the email form is complete for send

        :returns: True if the validator passed, otherwise False
        """
        if not self.email_recipients_and_responsibles:
            message = _("No email recipients selected")
            self.add_status_message(message, "error")
        if not self.email_subject:
            message = _("Please add an email subject")
            self.add_status_message(message, "error")
        if not self.email_body:
            message = _("Please add an email text")
            self.add_status_message(message, "error")
        if not self.reports:
            message = _("No reports found")
            self.add_status_message(message, "error")

        if not all([self.email_recipients_and_responsibles,
                    self.email_subject,
                    self.email_body,
                    self.reports]):
            return False
        return True

    def validate_email_size(self):
        """Validate if the email size exceeded the max. allowed size

        :returns: True if the validator passed, otherwise False
        """
        if self.total_size > self.max_email_size:
            # don't allow to send oversized emails
            self.allow_send = False
            message = _("Total size of email exceeded {:.1f} MB ({:.2f} MB)"
                        .format(self.max_email_size / 1024,
                                self.total_size / 1024))
            self.add_status_message(message, "error")
            return False
        return True

    def validate_email_recipients(self):
        """Validate if the recipients are all valid

        :returns: True if the validator passed, otherwise False
        """
        # inform the user about invalid recipients
        if not all(map(lambda r: r.get("valid"), self.recipients_data)):
            message = _(
                "Not all contacts are equal for the selected Reports. "
                "Please manually select recipients for this email.")
            self.add_status_message(message, "warning")
            return False
        return True

    @property
    def portal(self):
        """Get the portal object
        """
        return api.get_portal()

    @property
    def laboratory(self):
        """Laboratory object from the LIMS setup
        """
        return api.get_setup().laboratory

    @property
    @view.memoize
    def reports(self):
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

    @property
    @view.memoize
    def attachments(self):
        """Return the objects from the UIDs given in the request
        """
        uids = self.request.form.get("attachment_uids", [])
        return map(self.get_object_by_uid, uids)

    @property
    def email_sender_address(self):
        """Sender email is either the lab email or portal email "from" address
        """
        lab_email = self.laboratory.getEmailAddress()
        portal_email = self.portal.email_from_address
        return lab_email or portal_email

    @property
    def email_sender_name(self):
        """Sender name is either the lab name or the portal email "from" name
        """
        lab_from_name = self.laboratory.getName()
        portal_from_name = self.portal.email_from_name
        return lab_from_name or portal_from_name

    @property
    def email_recipients_and_responsibles(self):
        """Returns a unified list of recipients and responsibles
        """
        return list(set(self.email_recipients + self.email_responsibles))

    @property
    def email_recipients(self):
        """Email addresses of the selected recipients
        """
        return map(safe_unicode, self.request.form.get("recipients", []))

    @property
    def email_responsibles(self):
        """Email addresses of the responsible persons
        """
        return map(safe_unicode, self.request.form.get("responsibles", []))

    @property
    def email_subject(self):
        """Email subject line to be used in the template
        """
        # request parameter has precedence
        subject = self.request.get("subject", None)
        if subject is not None:
            return subject
        subject = self.context.translate(_("Analysis Results for {}"))
        return subject.format(self.client_name)

    @property
    def email_body(self):
        """Email body text to be used in the template
        """
        # request parameter has precedence
        body = self.request.get("body", None)
        if body is not None:
            return body
        return self.context.translate(_(self.email_template(self)))

    @property
    def email_attachments(self):
        attachments = []

        # Convert report PDFs -> email attachments
        for report in self.reports:
            pdf = self.get_pdf(report)
            if pdf is None:
                logger.error("Skipping empty PDF for report {}"
                             .format(report.getId()))
                continue
            sample = report.getAnalysisRequest()
            filename = "{}.pdf".format(api.get_id(sample))
            filedata = pdf.data
            attachments.append(
                mailapi.to_email_attachment(filedata, filename))

        # Convert additional attachments
        for attachment in self.attachments:
            af = attachment.getAttachmentFile()
            filedata = af.data
            filename = af.filename
            attachments.append(
                mailapi.to_email_attachment(filedata, filename))

        return attachments

    @property
    def reports_data(self):
        """Returns a list of report data dictionaries
        """
        reports = self.reports
        return map(self.get_report_data, reports)

    @property
    def recipients_data(self):
        """Returns a list of recipients data dictionaries
        """
        reports = self.reports
        return self.get_recipients_data(reports)

    @property
    def responsibles_data(self):
        """Returns a list of responsibles data dictionaries
        """
        reports = self.reports
        return self.get_responsibles_data(reports)

    @property
    def client_name(self):
        """Returns the client name
        """
        return safe_unicode(self.context.Title())

    @property
    def exit_url(self):
        """Exit URL for redirect
        """
        return "{}/{}".format(
            api.get_url(self.context), "reports_listing")

    @property
    def total_size(self):
        """Total size of all report PDFs + additional attachments
        """
        reports = self.reports
        attachments = self.attachments
        return self.get_total_size(reports, attachments)

    @property
    def max_email_size(self):
        """Return the max. allowed email size in KB
        """
        # check first if a registry record exists
        max_email_size = api.get_registry_record(
            "senaite.core.max_email_size")
        if max_email_size is None:
            max_size = DEFAULT_MAX_EMAIL_SIZE
        if max_size < 0:
            max_email_size = 0
        return max_size * 1024

    def make_sendlog_record(self, **kw):
        """Create a new sendlog record
        """
        user = get_user()
        actor = get_user_id()
        userprops = api.get_user_properties(user)
        actor_fullname = userprops.get("fullname", actor)
        email_send_date = DateTime()
        email_recipients = self.email_recipients
        email_responsibles = self.email_responsibles
        email_subject = self.email_subject
        email_body = self.render_email_template(self.email_body)
        email_attachments = map(api.get_uid, self.attachments)

        record = {
            "actor": actor,
            "actor_fullname": actor_fullname,
            "email_send_date": email_send_date,
            "email_recipients": email_recipients,
            "email_responsibles": email_responsibles,
            "email_subject": email_subject,
            "email_body": email_body,
            "email_attachments": email_attachments,

        }
        # keywords take precedence
        record.update(kw)
        return record

    def write_sendlog(self):
        """Write email sendlog
        """
        timestamp = DateTime()

        for report in self.reports:
            # get the current sendlog records
            records = report.getSendLog()
            # create a new record with the current data
            new_record = self.make_sendlog_record(email_send_date=timestamp)
            # set the new record to the existing records
            records.append(new_record)
            report.setSendLog(records)
            # reindex object to make changes visible in the snapshot
            report.reindexObject()
            # manually take a new snapshot
            take_snapshot(report)

    def publish_samples(self):
        """Publish all samples of the reports
        """
        samples = set()

        # collect primary + contained samples of the reports
        for report in self.reports:
            samples.add(report.getAnalysisRequest())
            samples.update(report.getContainedAnalysisRequests())

        # publish all samples + their partitions
        for sample in samples:
            self.publish(sample)

    def publish(self, sample):
        """Set status to prepublished/published/republished
        """
        wf = api.get_tool("portal_workflow")
        status = wf.getInfoFor(sample, "review_state")
        transitions = {"verified": "publish",
                       "published": "republish"}
        transition = transitions.get(status, "prepublish")
        logger.info("Transitioning sample {}: {} -> {}".format(
            api.get_id(sample), status, transition))
        try:
            # Manually update the view on the database to avoid conflict errors
            sample.getClient()._p_jar.sync()
            # Perform WF transition
            wf.doActionFor(sample, transition)
            # Commit the changes
            transaction.commit()
        except WorkflowException as e:
            logger.error(e)

    def render_email_template(self, template):
        """Return the rendered email template

        This method interpolates the $recipients variable with the selected
        recipients from the email form.

        :params template: Email body text
        :returns: Rendered email template
        """

        recipients = self.email_recipients_and_responsibles
        template_context = {
            "recipients": "\n".join(recipients)
        }

        email_template = Template(safe_unicode(template)).safe_substitute(
            **template_context)

        return email_template

    def send_email(self, recipients, subject, body, attachments=None):
        """Prepare and send email to the recipients

        :param recipients: a list of email or name,email strings
        :param subject: the email subject
        :param body: the email body
        :param attachments: list of email attachments
        :returns: True if all emails were sent, else False
        """
        email_body = self.render_email_template(body)

        success = []
        # Send one email per recipient
        for recipient in recipients:
            # N.B. we use just the email here to prevent this Postfix Error:
            # Recipient address rejected: User unknown in local recipient table
            pair = mailapi.parse_email_address(recipient)
            to_address = pair[1]
            mime_msg = mailapi.compose_email(self.email_sender_address,
                                             to_address,
                                             subject,
                                             email_body,
                                             attachments=attachments)
            sent = mailapi.send_email(mime_msg)
            if not sent:
                msg = _("Could not send email to {0} ({1})").format(pair[0],
                                                                    pair[1])
                self.add_status_message(msg, "warning")
                logger.error(msg)
            success.append(sent)

        if not all(success):
            return False
        return True

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def get_report_data(self, report):
        """Report data to be used in the template
        """
        sample = report.getAnalysisRequest()
        analyses = sample.getAnalyses(full_objects=True)
        # merge together sample + analyses attachments
        attachments = itertools.chain(
            sample.getAttachment(),
            *map(lambda an: an.getAttachment(), analyses))
        attachments_data = map(self.get_attachment_data, attachments)
        pdf = self.get_pdf(report)
        filesize = "{} Kb".format(self.get_filesize(pdf))
        filename = "{}.pdf".format(sample.getId())

        return {
            "sample": sample,
            "attachments": attachments_data,
            "pdf": pdf,
            "obj": report,
            "uid": api.get_uid(report),
            "filesize": filesize,
            "filename": filename,
        }

    def get_attachment_data(self, attachment):
        """Attachments data to be used in the template
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
            sample = report.getAnalysisRequest()
            # recipient names of this report
            report_recipient_names = []
            for recipient in self.get_recipients(sample):
                name = recipient.get("Fullname")
                email = recipient.get("EmailAddress")
                address = mailapi.to_email_address(email, name=name)
                record = {
                    "name": name,
                    "email": email,
                    "address": address,
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
                address = mailapi.to_email_address(email, name=name)
                record = {
                    "name": name,
                    "email": email,
                    "address": address,
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
        cc_emails = ar.getCCEmails(as_list=True)
        cc_emails = filter(None, map(recipient_from_email, cc_emails))

        return to + cc + cc_emails

    def ajax_recalculate_size(self):
        """Recalculate the total size of the selected attachments
        """
        reports = self.reports
        attachments = self.attachments
        total_size = self.get_total_size(reports, attachments)

        return {
            "files": len(reports) + len(attachments),
            "size": "%.2f" % total_size,
            "limit": self.max_email_size,
            "limit_exceeded": total_size > self.max_email_size,
        }

    def fail(self, message, status=500, **kw):
        """Set a JSON error object and a status to the response
        """
        self.request.response.setStatus(status)
        result = {"success": False, "errors": message, "status": status}
        result.update(kw)
        return result
