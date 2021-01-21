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
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_email_link
from bika.lims.utils import get_link
from Products.CMFCore.permissions import AddPortalContent
from senaite.app.listing import ListingView


class ClientsView(ListingView):
    """Listing view for Clients
    """

    def __init__(self, context, request):
        super(ClientsView, self).__init__(context, request)

        self.contentFilter = {
            "portal_type": "Client",
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        }

        self.title = self.context.translate(_("Clients"))

        self.show_select_column = True
        self.show_select_all_checkbox = False

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=Client",
                'permission': AddPortalContent,
                "icon": "add.png"
            }
        }

        self.columns = collections.OrderedDict((
            ("title", {
                "title": _("Name"),
                "index": "sortable_title"},),
            ("getClientID", {
                "title": _("Client ID")}),
            ("EmailAddress", {
                "title": _("Email Address"),
                "sortable": False}),
            ("getCountry", {
                "toggle": False,
                "sortable": False,
                "title": _("Country")}),
            ("getProvince", {
                "toggle": False,
                "sortable": False,
                "title": _("Province")}),
            ("getDistrict", {
                "toggle": False,
                "sortable": False,
                "title": _("District")}),
            ("Phone", {
                "title": _("Phone"),
                "sortable": False}),
            ("Fax", {
                "toggle": False,
                "sortable": False,
                "title": _("Fax")}),
            ("BulkDiscount", {
                "toggle": False,
                "sortable": False,
                "title": _("Bulk Discount")}),
            ("MemberDiscountApplies", {
                "toggle": False,
                "sortable": False,
                "title": _("Member Discount")}),
        ))

        self.review_states = [
            {
                "id": "default",
                "contentFilter": {"review_state": "active"},
                "title": _("Active"),
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {"review_state": "inactive"},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        """Applies new properties to the item (Client) that is currently being
        rendered as a row in the list

        :param obj: client to be rendered as a row in the list
        :param item: dict representation of the client, suitable for the list
        :param index: current position of the item within the list
        :type obj: CatalogBrain
        :type item: dict
        :type index: int
        :return: the dict representation of the item
        :rtype: dict
        """
        obj = api.get_object(obj)
        obj_url = self.get_client_url(obj)
        phone = obj.getPhone()
        item["replace"].update({
            "title": get_link(obj_url, api.get_title(obj)),
            "getClientID": get_link(obj_url, obj.getClientID()),
            "EmailAddress": get_email_link(obj.getEmailAddress()),
            "BulkDiscount": obj.getBulkDiscount(),
            "MemberDiscountApplies": obj.getMemberDiscountApplies(),
            "Phone": phone and get_link("tel:{}".format(phone), phone) or "",
        })
        return item

    def get_client_url(self, client):
        """Returns the url to the client's landing page
        """
        landing = self.get_client_landing_page()
        return "{}/{}".format(api.get_url(client), landing)

    def get_client_landing_page(self):
        """Returns the id of the view from inside Client to which the user has
        to be redirected when clicking to the link of a Client
        """
        record_key = "bika.lims.client.default_landing_page"
        return api.get_registry_record(record_key, default="analysisrequests")
