# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.supplyorderfolder import SupplyOrderFolderView
from bika.lims.permissions import AddSupplyOrder


class ClientOrdersView(SupplyOrderFolderView):
    """Client supply order listing
    """

    def __init__(self, context, request):
        super(ClientOrdersView, self).__init__(context, request)

        self.contentFilter = {
            "portal_type": "SupplyOrder",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(context),
                "level": 0
            }
        }
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=SupplyOrder",
                "permission": AddSupplyOrder,
                "icon": "++resource++bika.lims.images/add.png"
            }
        }

    def before_render(self):
        """Before template render hook
        """
