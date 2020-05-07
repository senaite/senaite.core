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

from Products.CMFCore.permissions import ModifyPortalContent
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import AddClient
from bika.lims.permissions import ManageAnalysisRequests
from bika.lims.utils import check_permission
from bika.lims.utils import get_email_link
from bika.lims.utils import get_link
from bika.lims.utils import get_registry_value


class ClientFolderContentsView(BikaListingView):
    """Listing view for all Clients
    """
    implements(IFolderContentsView)

    _LANDING_PAGE_REGISTRY_KEY = "bika.lims.client.default_landing_page"
    _DEFAULT_LANDING_PAGE = "analysisrequests"

    def __init__(self, context, request):
        super(ClientFolderContentsView, self).__init__(context, request)

        self.title = self.context.translate(_("Clients"))
        self.description = ""
        self.form_id = "list_clientsfolder"
        self.sort_on = "sortable_title"
        # Landing page to be added to the link of each client from the list
        self.landing_page = get_registry_value(
            self._LANDING_PAGE_REGISTRY_KEY, self._DEFAULT_LANDING_PAGE)

        self.contentFilter = {
            "portal_type": "Client",
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        }


        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.pagesize = 25
        self.icon = "{}/{}".format(
            self.portal_url, "++resource++bika.lims.images/client_big.png")
        request.set("disable_border", 1)

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
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {"review_state": "inactive"},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "transitions": [],
                "columns": self.columns.keys(),
            },
        ]

    def before_render(self):
        """Before template render hook
        """
        # Call `before_render` from the base class
        super(ClientFolderContentsView, self).before_render()

        # Render the Add button if the user has the AddClient permission
        if check_permission(AddClient, self.context):
            self.context_actions[_("Add")] = {
                "url": "createObject?type_name=Client",
                "icon": "++resource++bika.lims.images/add.png"
            }

        # Display a checkbox next to each client in the list if the user has
        # rights for ModifyPortalContent
        self.show_select_column = check_permission(ModifyPortalContent,
                                                   self.context)

    def isItemAllowed(self, obj):
        """Returns true if the current user has Manage AR rights for the
        current Client (item) to be rendered.

        :param obj: client to be rendered as a row in the list
        :type obj: ATContentType/DexterityContentType
        :return: True if the current user can see this Client. Otherwise, False.
        :rtype: bool
        """
        return check_permission(ManageAnalysisRequests, obj)

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
        # render a link to the defined start page
        link_url = "{}/{}".format(item["url"], self.landing_page)
        item["replace"]["title"] = get_link(link_url, item["title"])
        item["replace"]["getClientID"] = get_link(link_url, item["getClientID"])
        # render an email link
        item["replace"]["EmailAddress"] = get_email_link(item["EmailAddress"])
        # translate True/FALSE values
        item["replace"]["BulkDiscount"] = obj.getBulkDiscount() and _("Yes") or _("No")
        item["replace"]["MemberDiscountApplies"] = obj.getMemberDiscountApplies() and _("Yes") or _("No")
        # render a phone link
        phone = obj.getPhone()
        if phone:
            item["replace"]["Phone"] = get_link("tel:{}".format(phone), phone)

        return item


def client_match(client, search_term):
    # Check if the search_term matches some common fields
    if search_term in client.getClientID().lower():
        return True
    if search_term in client.Title().lower():
        return True
    if search_term in client.getName().lower():
        return True
    if search_term in client.Description().lower():
        return True
    return False
