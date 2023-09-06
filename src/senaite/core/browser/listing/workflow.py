# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.app.listing.adapters.workflow import ListingWorkflowTransition
from senaite.app.listing.interfaces import IListingWorkflowTransition
from zope.interface import implementer


@implementer(IListingWorkflowTransition)
class SampleReceiveWorkflowTransition(ListingWorkflowTransition):
    """Adapter to execute the workflow transitions "receive" for samples
    """
    def __init__(self, view, context, request):
        super(SampleReceiveWorkflowTransition, self).__init__(
            view, context, request)
        self.back_url = request.get_header("referer")

    def get_redirect_url(self):
        """Redirect after sample receive transition
        """
        if self.is_auto_partition_required():
            # Redirect to the partitioning view
            uid = api.get_uid(self.context)
            url = "{}/partition_magic?uids={}".format(self.back_url, uid)
            return url

        if self.is_auto_print_stickers_enabled():
            # Redirect to the auto-print stickers view
            uid = api.get_uid(self.context)
            url = "{}/sticker?autoprint=1&items={}".format(self.back_url, uid)
            return url

        # return default value
        return super(SampleReceiveWorkflowTransition, self).get_redirect_url()

    def is_auto_partition_required(self):
        """Returns whether the sample needs to be partitioned
        """
        template = self.context.getTemplate()
        return template and template.getAutoPartition()

    def is_auto_print_stickers_enabled(self):
        """Returns whether the auto print of stickers on reception is enabled
        """
        setup = api.get_setup()
        return "receive" in setup.getAutoPrintStickers()
