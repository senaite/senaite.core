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
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.permissions import AddAnalysisCategory
from senaite.app.listing import ListingView


class AnalysisCategoriesView(ListingView):

    def __init__(self, context, request):
        super(AnalysisCategoriesView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG

        self.contentFilter = {
            "portal_type": "AnalysisCategory",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            },
        }

        self.context_actions = {
            _("listing_analysiscategories_action_add", default="Add"): {
                "url": "++add++AnalysisCategory",
                "permission": AddAnalysisCategory,
                "icon": "senaite_theme/icon/plus"
            }
        }

        self.title = translate(_(
            "listing_analysiscategories_title",
            default="Analysis Categories")
        )
        self.description = ""
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/category_big.png"
        )

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _(
                    "listing_analysiscategories_column_title",
                    default="Category",
                ),
                "index": "sortable_title"}),
            ("Description", {
                "title": _(
                    "listing_analysiscategories_column_description",
                    default="Description",
                ),
                "index": "Description",
                "toggle": True,
            }),
            ("Department", {
                "title": _(
                    "listing_analysiscategories_column_department",
                    default="Department",
                ),
                "index": "department_title",
            }),
            ("SortKey", {
                "title": _(
                    "listing_analysiscategories_column_sort_key",
                    default="Sort Key",
                ),
                "sortable": True
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    "listing_analysiscategories_state_active",
                    default="Active",
                ),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _(
                    "listing_analysiscategories_state_inactive",
                    default="Inactive",
                ),
                "contentFilter": {'is_active': False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    "listing_analysiscategories_state_all",
                    default="All",
                ),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        obj = api.get_object(obj)

        item["replace"]["Title"] = get_link_for(obj)
        item["Description"] = obj.Description()
        item["SortKey"] = obj.getSortKey()

        department = obj.getDepartment()
        if department:
            item["replace"]["Department"] = get_link_for(department)

        return item
