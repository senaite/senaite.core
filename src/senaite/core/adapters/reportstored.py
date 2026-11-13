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

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.workflow import doActionFor
from senaite.core import logger
from senaite.core.interfaces import IReportStoredHandler
from zope.interface import implementer

# Transition to perform, depending on the current status of the sample. Any
# other status falls back to "prepublish"
TRANSITIONS = {
    "verified": "publish",
    "published": "republish",
}

DEFAULT_TRANSITION = "prepublish"


@implementer(IReportStoredHandler)
class PublishSamplesHandler(object):
    """Publishes the samples of the reports that have just been stored

    The report is the deliverable, so the samples it contains are published as
    soon as it exists. This runs within the transaction that creates the
    reports, so there is no window in which a report exists for a sample that
    is not published.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, reports):
        failed = []

        for sample in self.get_samples(reports):
            if not self.publish(sample):
                failed.append(sample)

        if failed:
            # Do not fail silently. The most likely reason to end up here is a
            # user without the permission to publish results
            ids = ", ".join(sorted(map(api.get_id, failed)))
            message = _("Could not publish: {}".format(ids))
            self.add_status_message(message, "warning")

    def get_samples(self, reports):
        """Returns the samples contained in the reports passed-in

        :param reports: the report objects
        :returns: list of unique sample objects
        """
        samples = {}
        for report in reports:
            contained = [report.getSample()] + report.getContainedSamples()
            for sample in filter(None, contained):
                samples[api.get_uid(sample)] = sample
        return list(samples.values())

    def publish(self, sample):
        """Transitions the sample to prepublished/published/republished

        :param sample: the sample to transition
        :returns: True if the transition was performed
        """
        status = api.get_review_status(sample)
        transition = TRANSITIONS.get(status, DEFAULT_TRANSITION)
        logger.info("Transitioning sample {}: {} -> {}".format(
            api.get_id(sample), status, transition))
        succeed, message = doActionFor(sample, transition)
        if not succeed:
            logger.warn("Could not transition sample {}: {}".format(
                api.get_id(sample), message))
        return succeed

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)
