# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims import workflow as wf
from bika.lims.browser import BrowserView, ulocalized_time
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.utils.analysisrequest import notify_rejection
from plone.memoize import view


class RejectSamplesView(BrowserView):
    """View that renders the Samples rejection view
    """
    template = ViewPageTemplateFile("templates/reject_samples.pt")

    def __init__(self, context, request):
        super(RejectSamplesView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.back_url = self.context.absolute_url()

    @property
    def is_notification_enabled(self):
        """Returns whether the notification on sample rejection is enabled
        """
        return api.get_setup().getNotifyOnSampleRejection()

    @property
    def is_rejection_workflow_enabled(self):
        """Return whether the rejection workflow is enabled
        """
        return api.get_setup().isRejectionWorkflowEnabled()

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)

        # Buttons
        form_continue = form.get("button_continue", False)
        form_cancel = form.get("button_cancel", False)

        # Is Rejection Workflow Enabled
        if not self.is_rejection_workflow_enabled:
            return self.redirect(message=_("Rejection workflow is not enabled"),
                                 level="warning")

        # Get the objects from request
        samples = self.get_samples_from_request()

        # No Samples selected
        if not samples:
            return self.redirect(message=_("No items selected"),
                                 level="warning")

        # Handle rejection
        if form_submitted and form_continue:
            logger.info("*** REJECT SAMPLES ***")
            processed = []
            for sample in form.get("samples", []):
                sample_uid = sample.get("uid", "")
                reasons = sample.get("reasons", [])
                other = sample.get("other_reasons", "")
                if not sample_uid:
                    continue

                # Omit if no rejection reason specified
                if not any([reasons, other]):
                    continue

                # This is quite bizarre!
                # AR's Rejection reasons is a RecordsField, but with one
                # record only, that contains both predefined and other reasons.
                obj = api.get_object_by_uid(sample_uid)
                rejection_reasons = {
                    "other": other,
                    "selected": reasons }
                obj.setRejectionReasons([rejection_reasons])
                wf.doActionFor(obj, "reject")
                processed.append(obj)

                # Client needs to be notified?
                if sample.get("notify", "") == "on":
                    notify_rejection(obj)

            if not processed:
                return self.redirect(message=_("No samples were rejected"))

            message = _("Rejected {} samples: {}").format(
                len(processed), ", ".join(map(api.get_id, processed)))
            return self.redirect(message=message)

        # Handle cancel
        if form_submitted and form_cancel:
            logger.info("*** CANCEL REJECTION ***")
            return self.redirect(message=_("Rejection cancelled"))

        return self.template()

    @view.memoize
    def get_samples_from_request(self):
        """Returns a list of objects coming from the "uids" request parameter
        """
        uids = self.request.form.get("uids", "")
        if isinstance(uids, basestring):
            uids = uids.split(",")

        uids = list(set(uids))
        if not uids:
            return []

        # Filter those analysis requests "reject" transition is allowed
        query = dict(portal_type="AnalysisRequest", UID=uids)
        brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
        samples = map(api.get_object, brains)
        return filter(lambda ob: wf.isTransitionAllowed(ob, "reject"), samples)

    @view.memoize
    def get_rejection_reasons(self):
        """Returns the list of available rejection reasons
        """
        return api.get_setup().getRejectionReasonsItems()

    def get_samples_data(self):
        """Returns a list of Samples data (dictionary)
        """
        for obj in self.get_samples_from_request():
            yield {
                "obj": obj,
                "id": api.get_id(obj),
                "uid": api.get_uid(obj),
                "title": api.get_title(obj),
                "path": api.get_path(obj),
                "url": api.get_url(obj),
                "sample_type": obj.getSampleTypeTitle(),
                "client_title": obj.getClientTitle(),
                "date": ulocalized_time(obj.created(), long_format=True),
            }

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
