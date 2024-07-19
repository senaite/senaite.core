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
from senaite.core.permissions import AddWorksheetTemplate
from senaite.core.i18n import translate
from senaite.app.listing import ListingView
from senaite.core.catalog import SETUP_CATALOG


class WorksheetTemplatesView(ListingView):
    """Listing View for Worksheet Templates
    """

    def __init__(self, context, request):
        super(WorksheetTemplatesView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG

        self.contentFilter = {
            "portal_type": "WorksheetTemplate",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            },
        }

        self.context_actions = {
            _(u"listing_worksheettemplates_action_add", default=u"Add"): {
                "url": "++add++WorksheetTemplate",
                "permission": AddWorksheetTemplate,
                "icon": "senaite_theme/icon/plus"
            }
        }

        self.title = translate(_(
            u"listing_worksheettemplates_title",
            default=u"Worksheet Templates")
        )
        self.icon = api.get_icon("WorksheetTemplates", html_tag=False)
        self.show_select_column = True

        self.columns = collections.OrderedDict((
            ("Name", {
                "title": _(
                    u"listing_worksheettemplates_column_name",
                    default=u"Name",
                ),
                "index": "sortable_title",
            }),
            ("Description", {
                "title": _(
                    u"listing_worksheettemplates_column_description",
                    default=u"Description"
                ),
                "toggle": True,
            }),
            ("Method", {
                "title": _(
                    u"listing_worksheettemplates_column_method",
                    default=u"Method"
                ),
                "toggle": True,
            }),
            ("Instrument", {
                "title": _(
                    u"listing_worksheettemplates_column_instrument",
                    default=u"Instrument"
                ),
                "index": "instrument_title",
                "toggle": True,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_worksheettemplates_state_active",
                    default=u"Active"
                ),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _(
                    u"listing_worksheettemplates_state_inactive",
                    default=u"Inactive"
                ),
                "contentFilter": {'is_active': False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    u"listing_worksheettemplates_state_all",
                    default=u"All"
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
        item["Description"] = api.get_description(obj)
        item["replace"]["Name"] = get_link_for(obj)

        instrument = obj.getInstrument()
        if instrument:
            instrument_title = api.get_title(instrument)
            item["Instrument"] = instrument_title
            item["replace"]["Instrument"] = get_link_for(instrument)

        method = obj.getRestrictToMethod()
        if method:
            method_title = api.get_title(method)
            item["Method"] = method_title
            item["replace"]["Method"] = get_link_for(method)

        return item
