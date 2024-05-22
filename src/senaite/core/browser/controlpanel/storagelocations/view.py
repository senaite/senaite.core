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
from bika.lims.utils import get_link_for
from senaite.core.i18n import translate
from senaite.app.listing import ListingView
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.permissions import AddStorageLocation


class StorageLocationsView(ListingView):

    def __init__(self, context, request):
        super(StorageLocationsView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG

        self.contentFilter = {
            "portal_type": "StorageLocation",
            "sort_on": "sortable_title",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            }
        }

        self.context_actions = {
            _("listing_storagelocations_action_add", default="Add"): {
                "url": "++add++StorageLocation",
                "permission": AddStorageLocation,
                "icon": "senaite_theme/icon/plus"
            }}

        self.title = translate(_(
            "listing_storagelocations_title",
            default="Storage Locations")
        )
        self.description = ""
        self.icon = api.get_icon("StorageLocations", html_tag=False)

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _(
                    "listing_storagelocations_column_title",
                    default="Storage Location",
                ),
                "index": "sortable_title",
            }),
            ("Description", {
                "title": _(
                    "listing_storagelocations_column_description",
                    default="Description",
                ),
                "index": "description",
                "toggle": True,
            }),
            ("SiteTitle", {
                "title": _(
                    "listing_storagelocations_column_site_title",
                    default="Site Title",
                ),
                "toggle": True,
            }),
            ("SiteCode", {
                "title": _(
                    "listing_storagelocations_column_site_code",
                    default="Site Code",
                ),
                "toggle": True,
            }),
            ("LocationTitle", {
                "title": _(
                    "listing_storagelocations_column_location_title",
                    default="Location Title",
                ),
                "toggle": True,
            }),
            ("LocationCode", {
                "title": _(
                    "listing_storagelocations_column_location_code",
                    default="Location Code",
                ),
                "toggle": True,
            }),
            ("ShelfTitle", {
                "title": _(
                    "listing_storagelocations_column_shelf_title",
                    default="Shelf Title",
                ),
                "toggle": True,
            }),
            ("ShelfCode", {
                "title": _(
                    "listing_storagelocations_column_shelf_code",
                    default="Shelf Code",
                ),
                "toggle": True,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    "listing_storagelocations_state_active",
                    default="Active",
                ),
                "contentFilter": {"is_active": True},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _(
                    "listing_storagelocations_state_inactive",
                    default="Inactive",
                ),
                "contentFilter": {"is_active": False},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    "listing_storagelocations_state_all",
                    default="All",
                ),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item["Description"] = api.get_description(obj)
        item["replace"]["Title"] = get_link_for(obj)

        item["SiteTitle"] = obj.getSiteTitle()
        item["SiteCode"] = obj.getSiteCode()
        item["LocationTitle"] = obj.getLocationTitle()
        item["LocationCode"] = obj.getLocationCode()
        item["ShelfTitle"] = obj.getShelfTitle()
        item["ShelfCode"] = obj.getShelfCode()

        return item
