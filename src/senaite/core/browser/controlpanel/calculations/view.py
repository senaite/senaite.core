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
from senaite.app.listing.view import ListingView
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.i18n import translate
from senaite.core.permissions import AddCalculation


class CalculationsView(ListingView):
    """Controlpanel Listing for Calculations
    """

    def __init__(self, context, request):
        super(CalculationsView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG

        self.contentFilter = {
            "portal_type": "Calculation",
            "sort_on": "sortable_title",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            },
        }

        self.context_actions = {
            _(u"listing_labproduct_action_add", default=u"Add"): {
                "url": "++add++Calculation",
                "permission": AddCalculation,
                "icon": "senaite_theme/icon/plus"
            }
        }

        self.title = translate(_(
            u"listing_calculations_title",
            default=u"Calculations")
        )

        self.icon = api.get_icon("Calculation", html_tag=False)
        self.show_select_column = True

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _(
                    u"listing_calculation_title",
                    default=u"Calculation",
                ),
                "index": "sortable_title",
            }),
            ("Description", {
                "title": _(
                    u"listing_calculation_description",
                    default=u"Description",
                ),
                "toggle": True,
            }),
            ("Formula", {
                "title": _(
                    u"listing_calculation_formula",
                    default=u"Formula",
                ),
                "toggle": True,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_labproducts_state_active",
                    default=u"Active",
                ),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            },
            {
                "id": "inactive",
                "title": _(
                    u"listing_labproducts_state_inactive",
                    default=u"Inactive",
                ),
                "contentFilter": {'is_active': False},
                "columns": self.columns.keys(),
            },
            {
                "id": "all",
                "title": _(
                    u"listing_labproducts_state_all",
                    default=u"All",
                ),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item.update({
            "Description": api.get_description(obj),
            "Formula": obj.getFormula(),
        })
        item["replace"]["Title"] = get_link_for(obj)
        return item
