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

from string import Template

from bika.lims import _
from bika.lims import api
from bika.lims.api.mail import compose_email
from bika.lims.api.mail import is_valid_email_address
from bika.lims.interfaces import IContact
from bika.lims.utils import get_link_for
from bika.lims.workflow import doActionFor as do_action_for
from collections import OrderedDict
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.PlonePAS.tools.memberdata import MemberData
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
    def is_notification_enabled(self):
        """Returns whether the notification on sample invalidation is enabled
        """
        setup = api.get_setup()
        return setup.getNotifyOnSampleInvalidation()

    @property
    def is_reason_required(self):
        """Returns whether the introduction of a reason is required for the
        invalidation of a sample
        """
        setup = api.get_setup()
        return setup.getInvalidationReasonRequired()

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)
        form_invalidate = form.get("button_invalidate", False)
        form_cancel = form.get("button_cancel", False)

        # Handle invalidation
        if form_submitted and form_invalidate:

            for sample in form.get("samples", []):
                uid = sample.get("uid", "")
                reason = sample.get("reason", "").strip()
                notify = sample.get("notify", "") == "on"

                # invalidate
                sample = api.get_object_by_uid(uid)
                sample.setInvalidationReason(reason)
                success, msg = do_action_for(sample, "invalidate")
                if not success:
                    message = _(
                        "Cannot invalidate ${sample_id}: ${error}",
                        mapping={
                            "sample_id": api.get_id(sample),
                            "error": api.safe_unicode(msg)
                        })
                    self.add_status_message(message, level="warning")
                    continue

                # notify via email
                if notify:
                    self.send_invalidation_email(sample)

                return self.redirect()

        # Handle cancel
        if form_submitted and form_cancel:
            return self.redirect(message=_(
                "The invalidation process has been successfully cancelled."
            ))
        return self.template()

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
        recipients = list(recipients) + sample.getCCEmails(as_list=True)
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

    def send_invalidation_email(self, sample):
        """Sends an email about the invalidation to the contacts of the sample
        """
        try:
            email_message = self.get_invalidation_email(sample)
            host = api.get_tool("MailHost")
            host.send(email_message, immediate=True)
        except Exception as err_msg:
            message = _(
                "Cannot send email for ${sample_id}: ${error}",
                mapping={
                    "sample_id": api.get_id(sample),
                    "error": api.safe_unicode(err_msg)
                })
            self.add_status_message(message, level="warning")

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
              mapping={"sample_id": api.get_id(sample)}
        ))

        setup = api.get_setup()
        retest = sample.getRetest()
        lab_email = setup.laboratory.getEmailAddress()
        lab_address = setup.laboratory.getPrintAddress()
        body = Template(setup.getEmailBodySampleInvalidation())
        body = body.safe_substitute({
            "lab_address": "<br/>".join(lab_address),
            "sample_id": api.get_id(sample),
            "sample_link": get_link_for(sample, csrf=False),
            "retest_id": api.get_id(retest),
            "retest_link": get_link_for(retest, csrf=False),
            "reason": sample.getInvalidationReason(),
        })

        return compose_email(from_addr=lab_email, to_addr=recipients,
                             subj=subject, body=body, html=True)

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
