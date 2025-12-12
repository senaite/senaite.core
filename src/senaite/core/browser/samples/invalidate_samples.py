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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from collections import OrderedDict
from string import Template

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.PlonePAS.tools.memberdata import MemberData
from bika.lims import _
from bika.lims import api
from bika.lims.api.mail import compose_email
from bika.lims.api.mail import is_valid_email_address
from bika.lims.utils import get_link_for
from senaite.core.interfaces import IContact
from senaite.core.api import dtime
from senaite.core.api import workflow as wapi
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.i18n import translate as t


class InvalidateSamplesView(BrowserView):
    """View for the invalidation of samples
    """
    template = ViewPageTemplateFile("templates/invalidate_samples.pt")

    def __init__(self, context, request):
        super(InvalidateSamplesView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.portal = api.get_portal()
        self.back_url = api.get_url(self.context)

    @property
    def uids(self):
        """Returns the uids passed through the request
        """
        uids = self.request.form.get("uids", "")
        if api.is_string(uids):
            uids = uids.split(",")

        # Remove duplicates while keeping the order
        return list(OrderedDict.fromkeys(uids))

    @property
    def is_reason_required(self):
        """Returns whether the introduction of a reason is required for the
        invalidation of a sample
        """
        setup = api.get_senaite_setup()
        return setup.getInvalidationReasonRequired()

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)
        form_invalidate = form.get("button_invalidate", False)
        form_cancel = form.get("button_cancel", False)

        # Handle invalidation
        if form_submitted and form_invalidate:

            processed = OrderedDict()
            samples = form.get("samples", [])
            for sample in samples:
                uid = sample.get("uid", "")
                reason = sample.get("reason", "").strip()
                notify = sample.get("notify", "") == "on"

                # invalidate
                sample = api.get_object_by_uid(uid)
                if not self.invalidate(sample, comment=reason):
                    message = _(
                        "Cannot invalidate ${sample_id}: ${error}",
                        mapping={
                            "sample_id": api.get_id(sample),
                        })
                    self.add_status_message(message, level="warning")
                    continue

                # keep track of the transitioned samples and recipients
                processed[sample] = []

                # notify via email and keep track of notified samples
                if notify:
                    recipients = self.send_invalidation_email(sample)
                    processed[sample] = recipients

            if not processed:
                return self.redirect(message=_(
                    "No samples were invalidated. Please ensure samples are "
                    "selected and meet the criteria for invalidation."
                ), level="error")

            # get the success message
            message = self.get_success_message(processed)
            return self.redirect(message=message)

        # Handle cancel
        if form_submitted and form_cancel:
            return self.redirect(message=_(
                "The invalidation process has been successfully cancelled."
            ))
        return self.template()

    def get_success_message(self, processed):
        """Returns the success message for samples that have been processed
        """
        # get the sample objects
        samples = processed.keys()
        # get the ids
        sample_ids = list(map(api.get_id, samples))
        # get the list of samples that were successfully notified by email
        notified = [samp for samp in samples if processed.get(samp)]
        # we are only interested on ids
        notified = list(map(api.get_id, notified))

        if len(samples) == 1 and notified:
            return _(
                "Sample ${sample_id} was successfully invalidated, and a "
                "notification email has been sent to the following "
                "recipients: ${recipients}.",
                mapping={
                    "sample_id": sample_ids[0],
                    "recipients": processed.get(samples[0]),
                })

        if len(sample_ids) == 1:
            return _(
                "Sample ${sample_id} has been successfully invalidated.",
                mapping={"sample_id": sample_ids[0]}
            )

        if notified:
            return _(
                "Samples ${sample_ids} were successfully invalidated, with "
                "notification emails sent for the following: ${notified_ids}.",
                mapping={
                    "sample_ids": ", ".join(sample_ids),
                    "notified_ids": ", ".join(notified),
                }
            )

        return _(
            "Samples ${sample_ids} were successfully invalidated.",
            mapping={"sample_ids": ", ".join(sample_ids),}
        )

    def get_samples(self):
        """Returns a list of objects coming from the "uids" request parameter
        """
        # Remove samples that cannot be invalidated
        samples = []
        query = dict(portal_type="AnalysisRequest", UID=self.uids)
        for brain in api.search(query, SAMPLE_CATALOG):
            sample = api.get_object(brain)
            if wapi.is_transition_allowed(sample, "invalidate"):
                samples.append(sample)

        return samples

    def get_samples_data(self):
        """Returns a list of Samples data (dictionary)
        """
        for obj in self.get_samples():
            emails = self.get_recipients(obj)
            created = api.get_creation_date(obj)
            yield {
                "obj": obj,
                "id": api.get_id(obj),
                "uid": api.get_uid(obj),
                "title": api.get_title(obj),
                "path": api.get_path(obj),
                "url": api.get_url(obj),
                "sample_type": obj.getSampleTypeTitle(),
                "client_title": obj.getClientTitle(),
                "date": dtime.to_localized_time(created, long_format=True),
                "recipients": emails,
            }

    def get_recipients(self, sample):
        """Returns the list of email recipients for the given sample
        """
        managers = api.get_users_by_roles("LabManager")
        recipients = managers + [sample.getContact()] + sample.getCCContact()
        recipients = filter(None, map(self.get_email_address, recipients))
        recipients = list(OrderedDict.fromkeys(recipients))

        # extend with the CC emails
        recipients = recipients + sample.getCCEmails(as_list=True)
        recipients = filter(is_valid_email_address, recipients)
        return list(recipients)

    def get_email_address(self, contact_user_email):
        """Returns the email address for the contact, member or email
        """
        if is_valid_email_address(contact_user_email):
            return contact_user_email

        if IContact.providedBy(contact_user_email):
            contact_email = contact_user_email.getEmailAddress()
            return self.get_email_address(contact_email)

        if isinstance(contact_user_email, MemberData):
            contact_user_email = contact_user_email.getUser()

        if isinstance(contact_user_email, PloneUser):
            # Try with the contact's email first
            contact = api.get_user_contact(contact_user_email)
            contact_email = self.get_email_address(contact)
            if contact_email:
                return contact_email

            # Fallback to member's email
            user_email = contact_user_email.getProperty("email")
            return self.get_email_address(user_email)

        return None

    def invalidate(self, sample, comment=""):
        """Invalidates the sample and stores a comment in action as the reason
        of invalidation
        """
        wf = api.get_tool("portal_workflow")
        try:
            wf.doActionFor(sample, "invalidate", comment=comment)
            return True
        except WorkflowException:
            return False

    def send_invalidation_email(self, sample):
        """Sends an email about the invalidation to the contacts of the sample
        and if succeeds, returns back the email's "To" mime header. Returns
        None otherwise
        """
        try:
            email_message = self.get_invalidation_email(sample)
            host = api.get_tool("MailHost")
            host.send(email_message, immediate=True)
            return email_message["To"]
        except Exception as err_msg:
            message = _(
                "Cannot send email for ${sample_id}: ${error}",
                mapping={
                    "sample_id": api.get_id(sample),
                    "error": api.safe_unicode(err_msg)
                })
            self.add_status_message(message, level="warning")

        return None

    def get_invalidation_email(self, sample):
        """Returns the sample invalidation MIME Message for the sample
        """
        recipients = self.get_recipients(sample)
        if not recipients:
            sample_id = api.get_id(sample)
            raise ValueError("No valid recipients for {}".format(sample_id))

        # Compose the email
        subject = t(
            _("Erroneous result publication: ${sample_id}",
              mapping={"sample_id": api.get_id(sample)})
        )

        setup = api.get_senaite_setup()
        retest = sample.getRetest()
        lab_email = setup.laboratory.getEmailAddress()
        lab_address = setup.laboratory.getPrintAddress()
        body = Template(setup.getEmailBodySampleInvalidation())
        body = body.safe_substitute({
            "lab_address": u"<br/>".join(lab_address),
            "sample_id": api.get_id(sample),
            "sample_link": get_link_for(sample, csrf=False),
            "retest_id": api.get_id(retest),
            "retest_link": get_link_for(retest, csrf=False),
            "reason": self.get_invalidation_reason(sample),
        })

        return compose_email(from_addr=lab_email, to_addr=recipients,
                             subj=subject, body=body, html=True)

    def get_invalidation_reason(self, sample):
        """Returns the reason of the invalidation, if any. Returns empty string
        otherwise
        """
        history = api.get_review_history(sample)
        for event in history:
            if event.get("action") == "invalidate":
                return event.get("comments", "")
        return ""

    def redirect(self, redirect_url=None, message=None, level="info"):
        """Redirect with a message
        """
        if redirect_url is None:
            redirect_url = self.back_url
        if message is not None:
            self.add_status_message(message, level)
        return self.request.response.redirect(redirect_url)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)
