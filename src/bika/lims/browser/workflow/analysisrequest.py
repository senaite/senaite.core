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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from string import Template

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.api.mail import compose_email
from bika.lims.api.mail import is_valid_email_address
from bika.lims.browser.workflow import RequestContextAware
from bika.lims.browser.workflow import WorkflowActionGenericAdapter
from bika.lims.content.analysisspec import ResultsRangeDict
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IContact
from bika.lims.interfaces import IWorkflowActionUIDsAdapter
from bika.lims.utils import get_link_for
from collections import OrderedDict
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.PlonePAS.tools.memberdata import MemberData
from zope.interface import implements


class WorkflowActionCopyToNewAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'copy_to_new' action
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        url = "{}/ar_add?ar_count={}&copy_from={}".format(
            self.back_url, len(uids), ",".join(uids))
        return self.redirect(redirect_url=url)


class WorkflowActionPrintStickersAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'print_stickers' action
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        url = "{}/sticker?items={}".format(self.back_url, ",".join(uids))
        return self.redirect(redirect_url=url)


class WorkflowActionCreatePartitionsAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'copy_to_new' action
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        url = "{}/partition_magic?uids={}".format(self.back_url, ",".join(uids))
        return self.redirect(redirect_url=url)


class WorkflowActionPublishAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'publish'-like actions
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        uids = ",".join(uids)
        portal = api.get_portal()
        portal_url = api.get_url(portal)
        url = "{}/samples/publish?items={}".format(portal_url, uids)
        return self.redirect(redirect_url=url)


class WorkflowActionRejectAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of Analysis Requests 'reject' action
    """

    def __call__(self, action, objects):
        samples = filter(IAnalysisRequest.providedBy, objects)
        if samples:
            # Action reject applies to samples. Redirect to Sample Reject view
            uids = map(api.get_uid, samples)
            uids_str = ",".join(uids)
            url = "{}/reject_samples?uids={}".format(self.back_url, uids_str)
            return self.redirect(redirect_url=url)

        # Generic transition if reject applies to other types (e.g. Analysis)
        transitioned = self.do_action(action, objects)
        if not transitioned:
            return self.redirect(message=_("No changes made."), level="warning")

        # Redirect the user to success page
        ids =  map(api.get_id, transitioned)
        message = _("Rejected items: {}").format(", ".join(ids))
        return self.success(transitioned, message=message)


class WorkflowActionReceiveAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of Analysis Request receive action
    """

    def __call__(self, action, objects):
        transitioned = self.do_action(action, objects)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        auto_partitions = filter(self.is_auto_partition_required, objects)
        if auto_partitions:
            # Redirect to the partitioning view
            uids = ",".join(map(api.get_uid, auto_partitions))
            url = "{}/partition_magic?uids={}".format(self.back_url, uids)
            return self.redirect(redirect_url=url)

        if self.is_auto_print_stickers_enabled():
            # Redirect to the auto-print stickers view
            uids = ",".join(map(api.get_uid, transitioned))
            url = "{}/sticker?autoprint=1&items={}".format(self.back_url, uids)
            return self.redirect(redirect_url=url)

        # Redirect the user to success page
        return self.success(transitioned)

    def is_auto_partition_required(self, brain_or_object):
        """Returns whether the passed in object needs to be partitioned
        """
        obj = api.get_object(brain_or_object)
        if not IAnalysisRequest.providedBy(obj):
            return False
        template = obj.getTemplate()
        return template and template.getAutoPartition()

    def is_auto_print_stickers_enabled(self):
        """Returns whether the auto print of stickers on reception is enabled
        """
        return "receive" in self.context.bika_setup.getAutoPrintStickers()


class WorkflowActionInvalidateAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of Analysis Request invalidate action
    """

    def __call__(self, action, objects):
        transitioned = self.do_action(action, objects)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        # Need to notify client contacts?
        if not self.context.bika_setup.getNotifyOnSampleInvalidation():
            return self.success(transitioned)

        # Alert the client contacts who ordered the results, stating that a
        # possible mistake has been picked up and is under investigation.
        for sample in transitioned:
            self.send_invalidation_email(sample)

        # Redirect the user to success page
        return self.success(transitioned)

    def send_invalidation_email(self, sample):
        """Sends an email notification to sample's client contact if the sample
        passed in has a retest associated
        """
        retest = sample.getRetest()
        if not retest:
            logger.warn("No retest found for {}. And it should!"
                        .format(api.get_id(sample)))
            return

        # Send the email
        try:
            email_message = self.get_invalidation_email(sample)
            host = api.get_tool("MailHost")
            host.send(email_message, immediate=True)
        except Exception as err_msg:
            message = _(
                "Cannot send email for ${sample_id}: ${error}",
                mapping={
                    "sample_id": api.get_id(sample),
                    "error": safe_unicode(err_msg)
                })
            self.context.plone_utils.addPortalMessage(message, "warning")

    def get_invalidation_email(self, sample):
        """Returns the sample invalidation MIME Message for the sample
        """
        # Get the recipients
        managers = api.get_users_by_roles("LabManager")
        recipients = managers + [sample.getContact()] + sample.getCCContact()
        recipients = filter(None, map(self.get_email_address, recipients))
        recipients = list(OrderedDict.fromkeys(recipients))

        if not recipients:
            sample_id = api.get_id(sample)
            raise ValueError("No valid recipients for {}".format(sample_id))

        # Compose the email
        subject = self.context.translate(_(
            "Erroneous result publication: ${sample_id}",
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
        })

        return compose_email(from_addr=lab_email, to_addr=recipients,
                             subj=subject, body=body, html=True)

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


class WorkflowActionPrintSampleAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of Analysis Request print_sample action
    """

    def __call__(self, action, objects):
        # Update printed times
        transitioned = filter(lambda obj: self.set_printed_time(obj), objects)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        # Redirect the user to success page
        return self.success(transitioned)

    def set_printed_time(self, sample):
        """Updates the printed time of the last results report from the sample
        """
        if api.get_workflow_status_of(sample) != "published":
            return False

        reports = sample.objectIds("ARReport")
        if not reports:
            return False

        last_report = sample.get(reports[-1])
        last_report.setDatePrinted(DateTime())
        sample.reindexObject(idxs=["getPrinted"])
        return True


class WorkflowActionSampleAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of Analysis Request sample action
    """

    def __call__(self, action, objects):
        # Assign the Sampler and DateSampled
        for obj in objects:
            try:
                self.set_sampler_info(obj)
            except ValueError as e:
                return self.redirect(message=str(e), level="warning")

        # Trigger "sample" transition
        transitioned = self.do_action(action, objects)
        if not transitioned:
            message = _("Could not transition samples to the sampled state")
            return self.redirect(message=message, level="warning")

        # Redirect the user to success page
        return self.success(transitioned)

    def set_sampler_info(self, sample):
        """Updates the Sampler and the Sample Date with the values provided in
        the request. If neither Sampler nor SampleDate are present in the
        request, returns False
        """
        if sample.getSampler() and sample.getDateSampled():
            # Sampler and Date Sampled already set. This is correct
            return True

        # Try to get the sampler and date sampled from the request.
        # This might happen when the "Sample" transition is triggered from the
        # samples listing view (form keys == column names of the listing)

        # try to get the sampler from the request
        sampler = self.get_form_value("getSampler", sample,
                                      sample.getSampler())
        if not sampler:
            sid = api.get_id(sample)
            raise ValueError(_("Sampler required for sample %s" % sid))

        # try to get the date sampled from the request
        sampled = self.get_form_value("getDateSampled", sample,
                                      sample.getDateSampled())
        if not sampled:
            sid = api.get_id(sample)
            raise ValueError(_("Sample date required for sample %s" % sid))

        # set the field values
        sample.setSampler(sampler)
        sample.setDateSampled(sampled)

        return True


class WorkflowActionPreserveAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of Analysis Request preserve action
    """

    def __call__(self, action, objects):
        # Assign the Preserver and DatePreserved
        transitioned = filter(lambda obj: self.set_preserver_info(obj), objects)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        # Trigger "preserve" transition
        transitioned = self.do_action(action, transitioned)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        # Redirect the user to success page
        return self.success(transitioned)

    def set_preserver_info(self, sample):
        """Updates the Preserver and the Date Preserved with the values provided
        in the request. If neither Preserver nor DatePreserved are present in
        the request, returns False
        """
        if sample.getPreserver() and sample.getDatePreserved():
            # Preserver and Date Preserved already set. This is correct
            return True
        preserver = self.get_form_value("Preserver", sample,
                                        sample.getPreserver())
        preserved = self.get_form_value("getDatePreserved",
                                        sample.getDatePreserved())
        if not all([preserver, preserved]):
            return False
        sample.setPreserver(preserver)
        sample.setDatePreserver(DateTime(preserved))
        return True


class WorkflowActionScheduleSamplingAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of Analysis request schedule sampling action
    """

    def __call__(self, action, objects):
        # Assign the scheduled Sampler and Sampling Date
        transitioned = filter(lambda obj: self.set_sampling_info(obj), objects)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        # Trigger "schedule_sampling" transition
        transitioned = self.do_action(action, transitioned)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        # Redirect the user to success page
        return self.success(transitioned)

    def set_sampling_info(self, sample):
        """Updates the scheduled Sampling sampler and the Sampling Date with the
        values provided in the request. If neither Sampling sampler nor Sampling
        Date are present in the request, returns False
        """
        if sample.getScheduledSamplingSampler() and sample.getSamplingDate():
            return True
        sampler = self.get_form_value("getScheduledSamplingSampler", sample,
                                      sample.getScheduledSamplingSampler())
        sampled = self.get_form_value("getSamplingDate",
                                      sample.getSamplingDate())
        if not all([sampler, sampled]):
            return False
        sample.setScheduledSamplingSampler(sampler)
        sample.setSamplingDate(DateTime(sampled))
        return True


class WorkflowActionSaveAnalysesAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of "save analyses" action in Analysis Request.
    """

    def __call__(self, action, objects):
        """The objects passed in are Analysis Services and the context is the
        Analysis Request
        """
        sample = self.context
        if not IAnalysisRequest.providedBy(sample):
            return self.redirect(message=_("No changes made"), level="warning")

        # NOTE: https://github.com/senaite/senaite.core/issues/1276
        #
        # Explicitly lookup the UIDs from the request, because the default
        # behavior of the method `get_uids` in `WorkflowActionGenericAdapter`
        # falls back to the UID of the current context if no UIDs were
        # submitted, which is in that case an `AnalysisRequest`.
        uids = self.get_uids_from_request()
        services = map(api.get_object, uids)

        # Get form values
        form = self.request.form
        prices = form.get("Price", [None])[0]
        hidden = map(lambda o: {
            "uid": api.get_uid(o), "hidden": self.is_hidden(o)
        }, services)

        # Do not overwrite default result ranges set through sample
        # specification field unless the edition of specs at analysis
        # level is explicitely allowed
        specs = []
        if self.is_ar_specs_enabled:
            specs = map(lambda service: self.get_specs(service), services)

        # Set new analyses to the sample
        sample.setAnalysisServicesSettings(hidden)
        sample.setAnalyses(uids, prices=prices, specs=specs, hidden=hidden)

        # Just in case new analyses have been added while the Sample was in a
        # "non-open" state (e.g. "to_be_verified")
        self.do_action("rollback_to_receive", [sample])

        # Reindex the analyses that have been added
        for analysis in sample.objectValues("Analysis"):
            analysis.reindexObject()

        # Reindex the Sample
        sample.reindexObject()

        # Redirect the user to success page
        self.success([sample])

    @property
    def is_ar_specs_enabled(self):
        """Returns whether the assignment of specs at analysis level within
        sample context is enabled or not
        """
        setup = api.get_setup()
        return setup.getEnableARSpecs()

    def is_hidden(self, service):
        """Returns whether the request Hidden param for the given obj is True
        """
        uid = api.get_uid(service)
        hidden_ans = self.request.form.get("Hidden", {})
        return hidden_ans.get(uid, "") == "on"

    def get_specs(self, service):
        """Returns the analysis specs available in the request for the given uid
        """
        uid = api.get_uid(service)
        keyword = service.getKeyword()
        specs = ResultsRangeDict(keyword=keyword, uid=uid).copy()
        for key in specs.keys():
            specs_value = self.request.form.get(key, [{}])[0].get(uid, None)
            specs[key] = specs_value or specs.get(key)
        return specs
