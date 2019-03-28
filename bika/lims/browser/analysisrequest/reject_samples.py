# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims import workflow as wf
from bika.lims.browser import BrowserView, ulocalized_time
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
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

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)

        # Buttons
        form_continue = form.get("button_continue", False)
        form_cancel = form.get("button_cancel", False)

        # Is Rejection Workflow Enabled
        if not api.get_setup().isRejectionWorkflowEnabled():
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
            logger.info("*** REJECT SAMPLES (1 of 2) ***")

            selected_samples = []


            if not selected_samples:
                return self.redirect(message=_("No samples were rejected"))

            message = _("Rejected {} samples: {}").format(
                len(samples), ", ".join(map(api.get_id, selected_samples)))
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
            obj = api.get_object(obj)
            yield {
                "obj": obj,
                "id": api.get_id(obj),
                "uid": api.get_uid(obj),
                "title": api.get_title(obj),
                "path": api.get_path(obj),
                "url": api.get_url(obj),
                "sample_type": api.get_title(obj.getSampleType()),
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
