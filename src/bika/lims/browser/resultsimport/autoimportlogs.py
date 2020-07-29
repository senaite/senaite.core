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

from bika.lims import bikaMessageFactory as _
from bika.lims.catalog import CATALOG_AUTOIMPORTLOGS_LISTING
from senaite.app.listing import ListingView


class AutoImportLogsView(ListingView):
    """Display all auto import logs
    """
    def __init__(self, context, request):
        super(AutoImportLogsView, self).__init__(context, request)
        self.catalog = CATALOG_AUTOIMPORTLOGS_LISTING
        self.contentFilter = {
            "portal_type": "AutoImportLog",
            "sort_on": "created",
            "sort_order": "descending"
        }
        self.context_actions = {}
        self.title = self.context.translate(_("Last Auto-Import Logs"))
        self.description = ""

        self.columns = OrderedDict((
            ("ImportTime", {
                "title": _("Time"),
                "sortable": False
            }),
            ("Instrument", {
                "title": _("Instrument"),
                "sortable": False,
                "attr": "getInstrumentTitle",
                "replace_url": "getInstrumentUrl"
            }),
            ("Interface", {
                "title": _("Interface"),
                "sortable": False,
                "attr": "getInterface",
            }),
            ("ImportFile", {
                "title": _("Imported File"),
                "sortable": False,
                "attr": "getImportedFile",
            }),
            ("Results", {
                "title": _("Results"),
                "sortable": False,
                "attr": "getResults"
            })
        ))

        self.review_states = [
            {
                "id": "default",
                "title":  _("All"),
                "contentFilter": {},
                "columns": self.columns.keys()
            },
        ]

    def folderitem(self, obj, item, index):
        item["ImportTime"] = obj.getLogTime.strftime("%Y-%m-%d H:%M:%S")
        return item
