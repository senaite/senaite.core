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


class SampleContainersView(ListingView):
    """Displays all available sample containers in a table
    """

    def __init__(self, context, request):
        super(SampleContainersView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG

        self.contentFilter = {
            "portal_type": "SampleContainer",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            },
        }

        self.context_actions = {
            _("listing_sampleconatiners_action_add", default="Add"): {
                "url": "++add++SampleContainer",
                "icon": "senaite_theme/icon/plus",
            }}

        self.title = translate(_(
            "listing_sampleconatiners_title",
            default="Sample Containers")
        )
        self.icon = api.get_icon("SampleContainers", html_tag=False)
        self.show_select_column = True

        self.columns = collections.OrderedDict((
            ("title", {
                "title": _(
                    u"listing_sampleconatiners_column_title",
                    default=u"Container"
                ),
                "index": "sortable_title",
            }),
            ("description", {
                "title": _(
                    u"listing_sampleconatiners_column_description",
                    default=u"Description"
                ),
                "toggle": True,
            }),
            ("containertype", {
                "title": _(
                    u"listing_sampleconatiners_column_containertype",
                    default=u"Container Type"
                ),
                "toggle": True,
            }),
            ("capacity", {
                "title": _(
                    u"listing_sampleconatiners_column_capacity",
                    default=u"Capacity"
                ),
                "toggle": True,
            }),
            ("pre_preserved", {
                "title": _(
                    u"listing_sampleconatiners_column_pre_preserved",
                    default=u"Pre-preserved"
                ),
                "toggle": True,
            }),
            ("security_seal_intact", {
                "title": _(
                    u"listing_sampleconatiners_column_security_seal_intact",
                    default=u"Security seal intact"
                ),
                "toggle": True,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_sampleconatiners_state_active",
                    default=u"Active"
                ),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _(
                    u"listing_sampleconatiners_state_inactive",
                    default=u"Inactive"
                ),
                "contentFilter": {'is_active': False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    u"listing_sampleconatiners_state_all",
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

        item["replace"]["title"] = get_link_for(obj)
        item["description"] = api.get_description(obj)

        # container type
        containertype = obj.getContainerType()
        if containertype:
            item["containertype"] = containertype.title
            item["replace"]["containertype"] = get_link_for(containertype)

        # capacity
        item["capacity"] = obj.getCapacity()

        # pre-preserved and preservation
        if obj.getPrePreserved():
            preservation = obj.getPreservation()
            if preservation:
                item["after"]["pre_preserved"] = get_link_for(preservation)

        if obj.getSecuritySealIntact():
            item["security_seal_intact"] = _("Yes")
        else:
            item["security_seal_intact"] = _("No")

        return item
