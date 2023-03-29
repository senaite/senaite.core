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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_link_for
from senaite.app.listing import ListingView


class SampleContainersView(ListingView):
    """Displays all available sample containers in a table
    """

    def __init__(self, context, request):
        super(SampleContainersView, self).__init__(context, request)

        self.contentFilter = {
            "portal_type": "SampleContainer",
            "sort_on": "sortable_title",
        }

        self.context_actions = {
            _("Add"): {
                "url": "++add++SampleContainer",
                "icon": "++resource++bika.lims.images/add.png",
            }}

        t = self.context.translate
        self.title = t(_("Sample Containers"))
        self.description = t(_(""))

        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("title", {
                "title": _("Container"),
                "index": "sortable_title"}),
            ("description", {
                "title": _("Description"),
                "index": "Description",
                "toggle": True,
            }),
            ("containertype", {
                "title": _("Container Type"),
                "toggle": True}),
            ("capacity", {
                "title": _("Capacity"),
                "toggle": True}),
            ("pre_preserved", {
                "title": _("Pre-preserved"),
                "toggle": True}),
            ("security_seal_intact", {
                "title": _("Security seal intact"),
                "toggle": True}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {'is_active': False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
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
