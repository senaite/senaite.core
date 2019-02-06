# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections
import json
from operator import itemgetter

import plone
from bika.lims import api
from bika.lims.api.security import check_permission
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
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
            "cancellation_state": "active"
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
            ("state_title", {
                "title": _("State"),
                "sortable": False, }),
            ("created", {
                "title": _("Created"), }),
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
                "contentFilter": {"cancellation_state": "cancelled"},
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
        title = api.get_title(obj)
        client = obj.getClient()
        created = api.get_creation_date(obj)
        date = obj.getBatchDate()

        item["BatchID"] = bid
        item["replace"]["BatchID"] = get_link(url, bid)
        item["Title"] = title
        item["replace"]["Title"] = get_link(url, title)
        item["created"] = self.ulocalized_time(created, long_format=True)
        item["BatchDate"] = self.ulocalized_time(date, long_format=True)

        if client:
            client_url = api.get_url(client)
            client_name = client.getName()
            item["Client"] = client_name
            item["replace"]["Client"] = get_link(client_url, client_name)

        return item


class ajaxGetBatches(BrowserView):
    """Vocabulary source for jquery combo dropdown box
    """

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request["searchTerm"].lower()
        page = self.request["page"]
        nr_rows = self.request["rows"]
        sord = self.request["sord"]
        sidx = self.request["sidx"]

        rows = []

        batches = self.bika_catalog(portal_type="Batch")

        for batch in batches:
            batch = batch.getObject()
            if self.portal_workflow.getInfoFor(
                    batch, "review_state", "open") != "open" or \
               self.portal_workflow.getInfoFor(
                   batch, "cancellation_state") == "cancelled":
                continue
            if batch.Title().lower().find(searchTerm) > -1 or \
               batch.Description().lower().find(searchTerm) > -1:
                rows.append({
                    "BatchID": batch.getBatchID(),
                    "Description": batch.Description(),
                    "BatchUID": batch.UID()})

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()),
                      key=itemgetter(sidx and sidx or "BatchID"))
        if sord == "desc":
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {
            "page": page,
            "total": pages,
            "records": len(rows),
            "rows": rows[
                (int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}

        return json.dumps(ret)
