# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from referencesamples import ReferenceSamplesView


class AddBlankView(ReferenceSamplesView):
    """Displays reference control samples
    """

    def __init__(self, context, request):
        super(AddBlankView, self).__init__(context, request)

        self.contentFilter = {
            "portal_type": "ReferenceSample",
            "getSupportedServices": self.get_assigned_services_uids(),
            "isValid": True,
            "getBlank": True,
            "review_state": "current",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.title = _("Add Blank Reference")
