# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.app.listing.adapters.workflow import ListingWorkflowTransition
from senaite.app.listing.interfaces import IListingWorkflowTransition
from zope.interface import implementer


@implementer(IListingWorkflowTransition)
class AnalysisRetractAdapter(ListingWorkflowTransition):

    def get_uids(self):
        """Return the uids affected by the retract transition
        """
        retest_uid = self.context.getRawRetest()
        uids = [api.get_uid(self.context), retest_uid]
        return filter(None, uids)


@implementer(IListingWorkflowTransition)
class AnalysisRetestAdapter(ListingWorkflowTransition):

    def get_uids(self):
        """Return the uids affected by the retest transition
        """
        retest_uid = self.context.getRawRetest()
        uids = [api.get_uid(self.context), retest_uid]
        return filter(None, uids)
