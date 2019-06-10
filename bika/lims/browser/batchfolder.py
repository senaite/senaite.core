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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from bika.lims import api
from bika.lims.api.security import check_permission
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import AddBatch
from bika.lims.utils import get_link


class BatchFolderContentsView(BikaListingView):
    """Listing View for all Batches in the System
    """

    def __init__(self, context, request):
        super(BatchFolderContentsView, self).__init__(context, request)

        self.catalog = "bika_catalog"
        self.contentFilter = {
            "portal_type": "Batch",
            "sort_on": "created",
            "sort_order": "descending",
            "is_active": True
        }

        self.context_actions = {}

        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.pagesize = 30

        batch_image_path = "/++resource++bika.lims.images/batch_big.png"
        self.icon = "{}{}".format(self.portal_url, batch_image_path)
        self.title = self.context.translate(_("Batches"))
        self.description = ""

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Title"),
                "index": "title", }),
            ("BatchID", {
                "title": _("Batch ID"),
                "index": "getId", }),
            ("Description", {
                "title": _("Description"),
                "sortable": False, }),
            ("BatchDate", {
                "title": _("Date"), }),
            ("Client", {
                "title": _("Client"),
                "index": "getClientTitle", }),
            ("ClientID", {
                "title": _("Client ID"),
                "index": "getClientID", }),
            ("ClientBatchID", {
                "title": _("Client Batch ID"),
                "index": "getClientBatchID", }),
            ("state_title", {
                "title": _("State"),
                "sortable": False, }),
            ("created", {
                "title": _("Created"),
                "index": "created",
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "contentFilter": {"review_state": "open"},
                "title": _("Open"),
                "transitions": [{"id": "close"}, {"id": "cancel"}],
                "columns": self.columns.keys(),
            }, {
                "id": "closed",
                "contentFilter": {"review_state": "closed"},
                "title": _("Closed"),
                "transitions": [{"id": "open"}],
                "columns": self.columns.keys(),
            }, {
                "id": "cancelled",
                "title": _("Cancelled"),
                "transitions": [{"id": "reinstate"}],
                "contentFilter": {"is_active": False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "transitions": [],
                "columns": self.columns.keys(),
            },
        ]

    def before_render(self):
        """Before template render hook
        """
        super(BatchFolderContentsView, self).before_render()

        if self.context.portal_type == "BatchFolder":
            self.request.set("disable_border", 1)

    def update(self):
        """Called before the listing renders
        """
        super(BatchFolderContentsView, self).update()

        if self.on_batch_folder() and self.can_add_batches():
            self.context_actions[_("Add")] = {
                "url": "createObject?type_name=Batch",
                "permission": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}

    def on_batch_folder(self):
        """Checks if the current context is a Batch folder
        """
        return self.context.portal_type == "BatchFolder"

    def can_add_batches(self):
        """Checks if the current user is allowed to add batches
        """
        return check_permission(AddBatch, self.context)

    def folderitem(self, obj, item, index):
        """Applies new properties to the item (Batch) that is currently being
        rendered as a row in the list

        :param obj: client to be rendered as a row in the list
        :param item: dict representation of the batch, suitable for the list
        :param index: current position of the item within the list
        :type obj: ATContentType/DexterityContentType
        :type item: dict
        :type index: int
        :return: the dict representation of the item
        :rtype: dict
        """

        obj = api.get_object(obj)
        url = "{}/analysisrequests".format(api.get_url(obj))
        bid = api.get_id(obj)
        cbid = obj.getClientBatchID()
        title = api.get_title(obj)
        client = obj.getClient()
        created = api.get_creation_date(obj)
        date = obj.getBatchDate()

        item["BatchID"] = bid
        item["ClientBatchID"] = cbid
        item["replace"]["BatchID"] = get_link(url, bid)
        item["Title"] = title
        item["replace"]["Title"] = get_link(url, title)
        item["created"] = self.ulocalized_time(created, long_format=True)
        item["BatchDate"] = self.ulocalized_time(date, long_format=True)

        if client:
            client_url = api.get_url(client)
            client_name = client.getName()
            client_id = client.getClientID()
            item["Client"] = client_name
            item["ClientID"] = client_id
            item["replace"]["Client"] = get_link(client_url, client_name)
            item["replace"]["ClientID"] = get_link(client_url, client_id)

        return item
