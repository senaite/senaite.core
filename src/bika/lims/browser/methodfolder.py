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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import AddMethod
from bika.lims.utils import check_permission
from bika.lims.utils import get_link
from bika.lims.utils import get_link_for


class MethodFolderContentsView(BikaListingView):
    """Listing view for all Methods
    """

    def __init__(self, context, request):
        super(MethodFolderContentsView, self).__init__(context, request)

        self.catalog = "senaite_catalog_setup"

        self.contentFilter = {
            "portal_type": "Method",
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        }

        self.context_actions = {}
        self.title = self.context.translate(_("Methods"))
        self.description = ""
        self.icon = "{}/{}".format(
            self.portal_url, "++resource++bika.lims.images/method_big.png")

        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Method"),
                "index": "sortable_title",
            }),
            ("Description", {
                "title": _("Description"),
                "index": "description",
                "toggle": True,
            }),
            ("Instruments", {
                "title": _("Instruments"),
                "toggle": True,
            }),
            ("Calculations", {
                "title": _("Calculations"),
                "toggle": True,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {'is_active': False},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def update(self):
        """Before template render hook
        """
        super(MethodFolderContentsView, self).update()

        # Render the Add button if the user has the AddMethod permission
        if check_permission(AddMethod, self.context):
            self.context_actions[_("Add")] = {
                "url": "createObject?type_name=Method",
                "icon": "++resource++bika.lims.images/add.png"
            }

    def folderitem(self, obj, item, index):
        """Applies new properties to the item (Client) that is currently being
        rendered as a row in the list

        :param obj: client to be rendered as a row in the list
        :param item: dict representation of the client, suitable for the list
        :param index: current position of the item within the list
        :type obj: ATContentType/DexterityContentType
        :type item: dict
        :type index: int
        :return: the dict representation of the item
        :rtype: dict
        """

        obj = api.get_object(obj)
        url = obj.absolute_url()
        title = obj.Title()

        item["replace"]["Title"] = get_link(url, value=title)

        instruments = obj.getInstruments()
        if instruments:
            titles = map(api.get_title, instruments)
            links = map(get_link_for, instruments)
            item["Insatruments"] = ",".join(titles)
            item["replace"]["Instruments"] = ", ".join(links)
        else:
            item["Instruments"] = ""

        calculations = obj.getCalculations()
        if calculations:
            titles = map(api.get_title, calculations)
            links = map(get_link_for, calculations)
            item["Calculations"] = ",".join(titles)
            item["replace"]["Calculations"] = ",".join(links)
        else:
            item["Calculations"] = ""

        return item
