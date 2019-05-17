# -*- coding: utf-8 -*-

import itertools

from bika.lims import _
from bika.lims import api
from bika.lims import logger
from bika.lims.browser.workflow import RequestContextAware
from bika.lims.interfaces import IWorkflowActionUIDsAdapter
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.component.interfaces import implements


class WorkflowActionPublishSamplesAdapter(RequestContextAware):
    """Adapter in charge of the client 'publish_samples' action
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        published = []

        # get the selected ARReport objects
        reports = map(api.get_object_by_uid, uids)
        # get all the contained sample UIDs of the generated PDFs
        sample_uids = map(self.get_sample_uids_in_report, reports)
        # uniquify the UIDs of the contained samples
        unique_sample_uids = set(list(
            itertools.chain.from_iterable(sample_uids)))

        # publish all the contained samples of the selected reports
        for uid in unique_sample_uids:
            sample = api.get_object_by_uid(uid)
            if self.publish_sample(sample):
                published.append(sample)

        # generate a status message of the published sample IDs
        message = _("No items published")
        if published:
            message = _("Published {}".format(
                ", ".join(map(api.get_id, published))))
        self.add_status_message(message, "info")

        return self.redirect(redirect_url=self.back_url)

    def get_sample_uids_in_report(self, report):
        """Return a list of contained sample UIDs
        """
        metadata = report.getMetadata() or {}
        return metadata.get("contained_requests", [])

    def publish_sample(self, sample):
        """Set status to prepublished/published/republished
        """
        wf = api.get_tool("portal_workflow")
        status = wf.getInfoFor(sample, "review_state")
        transitions = {"verified": "publish",
                       "published": "republish"}
        transition = transitions.get(status, "prepublish")
        logger.info("AR Transition: {} -> {}".format(status, transition))
        try:
            wf.doActionFor(sample, transition)
            return True
        except WorkflowException as e:
            logger.debug(e)
            return False

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)
