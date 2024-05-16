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
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import get_link
from senaite.app.listing import ListingView
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.i18n import translate
from senaite.core.permissions import AddSubGroup


class SubGroupsView(ListingView):

    def __init__(self, context, request):
        super(SubGroupsView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG
        self.show_select_column = True

        self.contentFilter = {
            "portal_type": "SubGroup",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            }
        }

        self.context_actions = {
            _("listing_subgroup_action_add", default="Add"): {
                "url": "++add++SubGroup",
                "permission": AddSubGroup,
                "icon": "senaite_theme/icon/plus"
            }
        }

        self.title = translate(_(
            "listing_subgroups_title",
            default="Sub-Groups")
        )
        self.description = ""
        self.icon = api.get_icon("SubGroups", html_tag=False)

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _(
                    "listing_subgroups_column_title",
                    default="Title"
                ),
                "index": "sortable_title"}),
            ("Description", {
                "title": _(
                    "listing_subgroups_column_description",
                    default="Description"
                ),
                "toggle": True,
            }),
            ("SortKey", {
                "title":  _(
                    "listing_subgroups_column_sortkey",
                    default="Sort Key"
                ),
                "toggle": True,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    "listing_subgroups_state_active",
                    default="Active"
                ),
                "contentFilter": {"is_active": True},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _(
                    "listing_subgroups_state_inactive",
                    default="Inactive"
                ),
                "contentFilter": {'is_active': False},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    "listing_subgroups_state_all",
                    default="All"
                ),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item["Description"] = obj.Description()
        item["replace"]["Title"] = get_link(item["url"], item["Title"])
        item["SortKey"] = obj.getSortKey()
        return item
