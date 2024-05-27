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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_link_for
from senaite.core.i18n import translate
from senaite.app.listing import ListingView
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.permissions import AddInstrumentType


class InstrumentTypesView(ListingView):

    def __init__(self, context, request):
        super(InstrumentTypesView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG

        self.contentFilter = {
            "portal_type": "InstrumentType",
            "sort_on": "sortable_title",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            },
        }

        self.context_actions = {
            _("listing_instrumenttypes_action_add", default="Add"): {
                "url": "++add++InstrumentType",
                "permission": AddInstrumentType,
                "icon": "senaite_theme/icon/plus"
            }
        }

        self.title = translate(_(
            "listing_instrumenttypes_title",
            default="Instrument Types")
        )
        self.icon = api.get_icon("InstrumentTypes", html_tag=False)
        self.show_select_column = True

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _(
                    "listing_instrumenttypes_column_title",
                    default="Title",
                ),
                "index": "sortable_title",
            }),
            ("Description", {
                "title": _(
                    "listing_instrumenttypes_column_description",
                    default="Description"
                ),
                "toggle": True,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    "listing_instrumenttypes_state_active",
                    default="Active",
                ),
                "contentFilter": {"is_active": True},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _(
                    "listing_instrumenttypes_state_inactive",
                    default="Inactive",
                ),
                "contentFilter": {'is_active': False},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    "listing_instrumenttypes_state_all",
                    default="All",
                ),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)

        item["replace"]["Title"] = get_link_for(obj)
        item["Description"] = api.get_description(obj)

        return item
