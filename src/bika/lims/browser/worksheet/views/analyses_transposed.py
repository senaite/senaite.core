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

from collections import OrderedDict

from bika.lims import _
from bika.lims.browser.worksheet.views import AnalysesView
from bika.lims.utils import get_link
from bika.lims.utils import t
from plone.memoize import view


class AnalysesTransposedView(AnalysesView):
    """Transposed Manage Results View for Worksheet Analyses
    """

    def __init__(self, context, request):
        super(AnalysesTransposedView, self).__init__(context, request)

        self.headers = OrderedDict()
        self.services = OrderedDict()

    @view.memoize
    def get_slots(self):
        """Return the current used analyses positions
        """
        positions = map(
            lambda uid: self.get_item_slot(uid), self.get_analyses_uids())
        return map(lambda pos: str(pos), sorted(set(positions)))

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
        item = super(AnalysesTransposedView, self).folderitem(obj, item, index)

        pos = str(item["Pos"])
        service = item["Service"]
        review_state = item["review_state"]

        # Skip retracted folderitems and display only the retest
        if review_state in ["retracted"]:
            return item

        # Append info link after the service
        # see: bika.lims.site.coffee for the attached event handler
        item["before"]["Result"] = get_link(
            "analysisservice_info?service_uid={}&analysis_uid={}"
            .format(item["service_uid"], item["uid"]),
            value="<span class='glyphicon glyphicon-info-sign'></span>",
            css_class="service_info")

        # remember the column headers of the first row
        if "Pos" not in self.headers:
            self.headers["Pos"] = self.make_empty_item(
                column_key=t(_("Position")), item_key="Pos")
        if pos not in self.headers["Pos"]:
            header_item = self.make_empty_item()
            # Add the item with the Pos header
            header_item["replace"]["Pos"] = self.get_slot_header(item)
            self.headers["Pos"][pos] = header_item

        # remember the services, e.g. Calcium, Magnesium, Total Hardness etc.
        if service not in self.services:
            self.services[service] = self.make_empty_item(
                column_key=service, item_key="Result")
        if pos not in self.services[service]:
            # Add the item below its position
            self.services[service][pos] = item

        return item

    def folderitems(self):
        super(AnalysesTransposedView, self).folderitems()

        # Insert the "column key" column
        self.columns["column_key"] = {"title": ""}

        # Insert the columns for the slots
        for pos in self.get_slots():
            self.columns[pos] = {"title": "", "type": "transposed"}

        # Restrict visible columns
        self.review_states[0]["columns"] = ["column_key"] + self.get_slots()

        # transposed rows holder
        transposed = OrderedDict()

        # first row contains the HTML slot headers
        transposed.update(self.headers)

        # the collected services (Iron, Copper, Calcium...) come afterwards
        services = OrderedDict(reversed(self.services.items()))
        # the collected services (Iron, Copper, Calcium...) come afterwards
        transposed.update(services)

        # listing fixtures
        self.total = len(transposed.keys())
        self.show_select_column = False
        self.show_select_all_checkbox = False

        # return the transposed rows
        return transposed.values()
