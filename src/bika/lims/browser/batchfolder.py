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
from bika.lims.permissions import AddBatch
from bika.lims.utils import get_link
from bika.lims.utils import get_progress_bar_html
from plone.memoize import view
from Products.CMFCore.permissions import View
from senaite.app.listing import ListingView
from senaite.core.catalog import SENAITE_CATALOG


class BatchFolderContentsView(ListingView):
    """Listing view for Batches
    """

    def __init__(self, context, request):
        super(BatchFolderContentsView, self).__init__(context, request)

        self.catalog = SENAITE_CATALOG
        self.contentFilter = {
            "portal_type": "Batch",
            "sort_on": "created",
            "sort_order": "descending",
            "is_active": True,
        }

        self.title = self.context.translate(_("Batches"))
        self.description = ""

        self.show_select_column = True
        self.form_id = "batches"
        self.context_actions = {}
        self.icon = "{}{}".format(self.portal_url, "/senaite_theme/icon/batch")

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Title"),
                "index": "title", }),
            ("Progress", {
                "title": _("Progress"),
                "index": "getProgress",
                "sortable": True,
                "toggle": True}),
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
                "transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "closed",
                "contentFilter": {"review_state": "closed"},
                "title": _("Closed"),
                "transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "cancelled",
                "title": _("Cancelled"),
                "transitions": [],
                "contentFilter": {"is_active": False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "transitions": [],
                "columns": self.columns.keys(),
            },
        ]

    def update(self):
        """Before template render hook
        """
        super(BatchFolderContentsView, self).update()

        if self.can_add():
            # Add button. Note we set "View" as the permission, cause when no
            # permission is set, system fallback to "Add portal content" for
            # current context
            add_ico = "{}{}".format(self.portal_url, "/senaite_theme/icon/plus")
            self.context_actions = {
                _("Add"): {
                    "url": self.get_add_url(),
                    "permission": View,
                    "icon": add_ico
                }
            }

    @view.memoize
    def get_add_url(self):
        """Return the batch add URL
        """
        container = self.get_batches_container()
        return "{}/createObject?type_name=Batch".format(api.get_url(container))

    @view.memoize
    def get_batches_container(self):
        """Returns the container object where new batches will be added
        """
        return api.get_current_client() or self.context

    @view.memoize
    def can_add(self):
        """Returns whether the current user can add new batches or not
        """
        container = self.get_batches_container()
        if not api.security.check_permission(AddBatch, container):
            return False
        return True

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

        # total sample progress
        progress = obj.getProgress()
        item["Progress"] = progress
        item["replace"]["Progress"] = get_progress_bar_html(progress)

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
