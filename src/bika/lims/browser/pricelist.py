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

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.api.security import check_permission
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import AddPricelist
from bika.lims.utils import get_link
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PricelistsView(BikaListingView):
    """Listing view for Pricelists
    """

    def __init__(self, context, request):
        super(PricelistsView, self).__init__(context, request)

        self.catalog = "portal_catalog"

        self.contentFilter = {
            "portal_type": "Pricelist",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {}
        self.title = self.context.translate(_("Pricelists"))
        self.description = ""
        self.icon = "{}/{}".format(
            self.portal_url, "++resource++bika.lims.images/pricelist_big.png")

        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Title"),
                "index": "sortable_title"}),
            ("getEffectiveDate", {
                "title": _("Start Date"),
                "index": "getEffectiveDate",
                "toggle": True}),
            ("getExpirationDate", {
                "title": _("End Date"),
                "index": "getExpirationDate",
                "toggle": True}),
        ))

        now = DateTime()
        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {
                    "getEffectiveDate": {
                        "query": now,
                        "range": "max",
                    },
                    "getExpirationDate": {
                        "query": now,
                        "range": "min",
                    },
                    "is_active": True,
                },
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {
                    "getEffectiveDate": {
                        "query": now,
                        "range": "min",
                    },
                    "getExpirationDate": {
                        "query": now,
                        "range": "max",
                    },
                    "is_active": False,
                },
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            }
        ]

    def before_render(self):
        """Before template render hook
        """
        super(PricelistsView, self).before_render()
        # Render the Add button if the user has the AddPricelist permission
        if check_permission(AddPricelist, self.context):
            self.context_actions[_("Add")] = {
                "url": "createObject?type_name=Pricelist",
                "icon": "++resource++bika.lims.images/add.png"
            }
        # Don't allow any context actions on the Methods folder
        self.request.set("disable_border", 1)

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

        item["getEffectiveDate"] = self.ulocalized_time(
            obj.getEffectiveDate())

        item["getExpirationDate"] = self.ulocalized_time(
            obj.getExpirationDate())

        return item


class PricelistView(BrowserView):
    """Pricelist view
    """
    template = ViewPageTemplateFile("templates/pricelist_view.pt")
    lineitems_pt = ViewPageTemplateFile("templates/pricelist_content.pt")

    def __call__(self):
        self.items = self.context.objectValues()
        self.pricelist_content = self.lineitems_pt()
        return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class PricelistPrintView(PricelistView):
    """Pricelist print view
    """
    template = ViewPageTemplateFile("templates/pricelist_print.pt")
    lineitems_pt = ViewPageTemplateFile("templates/pricelist_content.pt")
