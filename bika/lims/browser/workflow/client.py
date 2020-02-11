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

import itertools

from bika.lims import _
from bika.lims import api
from bika.lims.browser.workflow import RequestContextAware
from bika.lims.interfaces import IWorkflowActionUIDsAdapter
from bika.lims.workflow import doActionFor
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

        # add the status message for the response
        self.add_status_message(message, "info")

        # redirect back
        referer = self.request.get_header("referer")
        return self.redirect(redirect_url=referer)

    def get_sample_uids_in_report(self, report):
        """Return a list of contained sample UIDs
        """
        metadata = report.getMetadata() or {}
        return metadata.get("contained_requests", [])

    def publish_sample(self, sample):
        """Set status to prepublished/published/republished
        """
        status = api.get_workflow_status_of(sample)
        transitions = {"verified": "publish", "published": "republish"}
        transition = transitions.get(status, "prepublish")
        succeed, message = doActionFor(sample, transition)
        return succeed
