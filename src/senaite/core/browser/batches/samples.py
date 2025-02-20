# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.core.browser.samples.view import SamplesView as BaseView


class SamplesView(BaseView):
    """Samples listing inside Batches
    """

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        self.contentFilter = {
            "portal_type": "AnalysisRequest",
            "getBatchUID": api.get_uid(self.context),
            "sort_on": "created",
            "sort_order": "reverse",
            "isRootAncestor": True,  # only root ancestors
        }
