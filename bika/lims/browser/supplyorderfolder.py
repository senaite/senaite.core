# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class SupplyOrderFolderView(BikaListingView):
    """Listing View for Supply Orders
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(SupplyOrderFolderView, self).__init__(context, request)

        self.contentFilter = {
            "portal_type": "SupplyOrder",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "sort_on": "sortable_title",
        }

        self.context_actions = {}

        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "orders"

        self.title = self.context.translate(_("Orders"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/supplyorder_big.png")

        self.columns = collections.OrderedDict((
            ("OrderNumber", {
                "title": _("Order Number")}),
            ("OrderDate", {
                "title": _("Order Date")}),
            ("DateDispatched", {
                "title": _("Date Dispatched")}),
            ("state_title", {
                "title": _("State")}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            }, {
                "id": "pending",
                "contentFilter": {"review_state": "pending"},
                "title": _("Pending"),
                "columns": self.columns.keys(),
            }, {
                "id": "dispatched",
                "contentFilter": {"review_state": "dispatched"},
                "title": _("Dispatched"),
                "columns": self.columns.keys(),
            },
        ]

    def before_render(self):
        """Before template render hook
        """
        super(SupplyOrderFolderView, self).before_render()
        # Don't allow any context actions
        self.request.set("disable_border", 1)

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        item["OrderNumber"] = obj.getOrderNumber()
        item["OrderDate"] = self.ulocalized_time(obj.getOrderDate())
        item["DateDispatched"] = self.ulocalized_time(obj.getDateDispatched())
        item["replace"]["OrderNumber"] = get_link(
            api.get_url(obj), obj.getOrderNumber())
        return item
