# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from collections import OrderedDict

from bika.lims.browser.worksheet.views import AnalysesView
from plone.memoize import view


class AnalysesTransposedView(AnalysesView):
    """Transposed Manage Results View for Worksheet Analyses
    """

    def __init__(self, context, request):
        super(AnalysesTransposedView, self).__init__(context, request)

        self.headers = OrderedDict()
        self.services = OrderedDict()

    @view.memoize
    def get_positions(self):
        """Return the current used analyses positions
        """
        positions = map(
            lambda uid: str(self.get_item_slot(uid)), self.get_analyses_uids())
        return sorted(set(positions))

    @view.memoize
    def get_analyses_uids(self):
        """Return assigned analyses UIDs
        """
        return self.context.getAnalysesUIDs()

    def make_empty_item(self, **kw):
        """Create a new empty item
        """
        item = {
            "uid": None,
            "before": {},
            "after": {},
            "replace": {},
            "allow_edit": [],
            "disabled": False,
            "state_class": "state-active",
        }
        item.update(**kw)
        return item

    def folderitem(self, obj, item, index):
        super(AnalysesTransposedView, self).folderitem(obj, item, index)

        pos = str(item["Pos"])
        service = item["Service"]

        # remember the headers
        if "Pos" not in self.headers:
            self.headers["Pos"] = self.make_empty_item(
                column_key="Positions", item_key="Pos")
        if pos not in self.headers["Pos"]:
            # Add the item with the Pos header
            item["replace"]["Pos"] = self.get_slot_header(item)
            self.headers["Pos"][pos] = item

        # remember the services
        if service not in self.services:
            self.services[service] = self.make_empty_item(
                column_key=service, item_key="Result")
        if pos not in self.services[service]:
            # Add the item below its position
            self.services[service][pos] = item

        return item

    def folderitems(self):
        super(AnalysesTransposedView, self).folderitems()

        # Reset the columns after the items have been generated by the parent
        # classes to ensure that we do not interfere with their logic.
        self.columns = OrderedDict()
        # Transposed column keys
        self.columns["column_key"] = {"title": ""}
        # Slot position columns
        for pos in self.get_positions():
            self.columns[pos] = {"title": "", "type": "transposed"}
        # Set new columns to the default review_state
        self.review_states[0]["columns"] = ["column_key"] + self.get_positions()

        # transposed rows holder
        transposed = OrderedDict()

        # first row contains the HTML slot headers
        transposed.update(self.headers)

        # the collected services (Iron, Copper, Calcium...) come afterwards
        transposed.update(self.services)

        # listing fixtures
        self.total = len(transposed.keys())
        self.show_select_column = False
        self.show_select_all_checkbox = False

        # return the transposed rows
        return transposed.values()
