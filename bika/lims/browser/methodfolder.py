# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import AddMethod
from bika.lims.utils import check_permission
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class MethodFolderContentsView(BikaListingView):
    """Listing view for all Clients
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(MethodFolderContentsView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"

        self.contentFilter = {
            "portal_type": "Method",
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        }

        self.context_actions = {}
        self.title = self.context.translate(_("Methods"))
        self.icon = "{}/{}".format(
            self.portal_url, "++resource++bika.lims.images/method_big.png")
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
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
            ("Instrument", {
                "title": _("Instrument"),
                "toggle": True,
            }),
            ("Calculation", {
                "title": _("Calculation"),
                "toggle": True,
            }),
            ("ManualEntry", {
                "title": _("Manual entry"),
                "toggle": True,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"inactive_state": "active"},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns,
            }, {
                "id": "inactive",
                "title": _("Dormant"),
                "contentFilter": {"inactive_state": "inactive"},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns,
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns,
            },
        ]

    def before_render(self):
        """Before template render hook
        """
        # Render the Add button if the user has the AddClient permission
        if check_permission(AddMethod, self.context):
            self.context_actions[_("Add")] = {
                "url": "createObject?type_name=Method",
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

        url = obj.absolute_url()
        title = obj.Title()

        item["replace"]["Title"] = get_link(url, value=title)

        instruments = obj.getInstruments()
        if instruments:
            links = map(
                lambda i: get_link(i.absolute_url(), i.Title()), instruments)
            item["replace"]["Instrument"] = ", ".join(links)
        else:
            item["Instrument"] = ""

        calculation = obj.getCalculation()
        if calculation:
            title = calculation.Title()
            url = calculation.absolute_url()
            item["Calculation"] = title
            item["replace"]["Calculation"] = get_link(url, value=title)
        else:
            item["Calculation"] = ""

        manual_entry_of_results_allowed = obj.isManualEntryOfResults()
        item["ManualEntry"] = manual_entry_of_results_allowed
        item["replace"]["ManualEntry"] = " "
        if manual_entry_of_results_allowed:
            item["replace"]["ManualEntry"] = get_image("ok.png")

        return item
