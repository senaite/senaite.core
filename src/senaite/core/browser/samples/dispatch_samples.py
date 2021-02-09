# -*- coding: utf-8 -*-

import collections
import six

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.workflow import isTransitionAllowed
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger


class DispatchSamplesView(BrowserView):
    """Action URL for the sample "dispatch" transition
    """
    template = ViewPageTemplateFile("templates/dispatch_samples.pt")

    def __init__(self, context, request):
        super(DispatchSamplesView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.portal = api.get_portal()
        self.back_url = api.get_url(self.context)

    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)
        form_dispatch = form.get("button_dispatch", False)
        form_cancel = form.get("button_cancel", False)

        # Handle book out
        if form_submitted and form_dispatch:
            logger.info("*** DISPATCH ***")
            comment = form.get("comment", "")
            if not comment:
                return self.redirect(
                    redirect_url=self.request.getHeader("http_referer"),
                    message=_("Please specify a reason"), level="error")
            samples = self.get_samples()

            for sample in samples:
                self.dispatch(sample, comment)
            return self.redirect()

        # Handle cancel
        if form_submitted and form_cancel:
            return self.redirect(message=_("Cancelled"))
        return self.template()

    def dispatch(self, sample, comment):
        """Dispatch the sample
        """
        wf = api.get_tool("portal_workflow")
        try:
            wf.doActionFor(sample, "dispatch", comment=comment)
            return True
        except WorkflowException:
            return False

    def uniquify_items(self, items):
        """Uniquify the items with sort order
        """
        unique = []
        for item in items:
            if item in unique:
                continue
            unique.append(item)
        return unique

    def get_partitions(self, sample):
        """Return dispatchable sample partitions
        """
        if not IAnalysisRequest.providedBy(sample):
            return []
        partitions = sample.getDescendants(all_descendants=False)
        return filter(
            lambda part: isTransitionAllowed(part, "dispatch"), partitions)

    def get_samples(self):
        """Extract the samples from the request UIDs

        This might be either a samples container or a sample context
        """

        # fetch objects from request
        objs = self.get_objects_from_request()

        samples = []

        for obj in objs:
            # when coming from the samples listing
            if IAnalysisRequest.providedBy(obj):
                samples.append(obj)
                samples.extend(self.get_partitions(obj))

        # when coming from the WF menu inside a sample
        if IAnalysisRequest.providedBy(self.context):
            samples.append(self.context)
            samples.extend(self.get_partitions(self.context))

        return self.uniquify_items(samples)

    def get_title(self, obj):
        """Return the object title as unicode
        """
        title = api.get_title(obj)
        return api.safe_unicode(title)

    def get_samples_data(self):
        """Returns a list of containers that can be moved
        """
        for obj in self.get_samples():
            obj = api.get_object(obj)
            yield {
                "obj": obj,
                "id": api.get_id(obj),
                "uid": api.get_uid(obj),
                "title": self.get_title(obj),
                "url": api.get_url(obj),
                "sample_type": obj.getSampleTypeTitle(),
            }

    def get_objects_from_request(self):
        """Returns a list of objects coming from the "uids" request parameter
        """
        unique_uids = self.get_uids_from_request()
        return filter(None, map(self.get_object_by_uid, unique_uids))

    def get_uids_from_request(self):
        """Return a list of uids from the request
        """
        uids = self.request.form.get("uids", "")
        if isinstance(uids, six.string_types):
            uids = uids.split(",")
        unique_uids = collections.OrderedDict().fromkeys(uids).keys()
        return filter(api.is_uid, unique_uids)

    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID #{} !!")
        return obj

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
