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
