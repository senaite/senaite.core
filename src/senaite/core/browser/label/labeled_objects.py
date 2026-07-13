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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import get_link_for
from plone.memoize import view
from senaite.core.i18n import translate as t
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.browser.listing.base import ListingView
from senaite.core.api import label as label_api
from senaite.core.catalog import LABEL_CATALOG
from senaite.core.interfaces import IHaveLabels


class LabeledObjectsView(ListingView):
    """Displays all available labels
    """

    def __init__(self, context, request):
        super(LabeledObjectsView, self).__init__(context, request)

        self.contentFilter = {
            "object_provides": IHaveLabels.__identifier__,
            "sort_on": "title",
        }
        self.catalog = LABEL_CATALOG

        self.context_actions = {}

        t = self.context.translate
        self.title = t(_("Labeled Objects"))
        self.description = t(_("List all objects with labels"))

        self.show_select_column = True
        self.show_all = False

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Title"),
                "index": "title"}),
            ("Type", {
                "title": _("Type"),
                "toggle": True,
                "index": "portal_type"}),
            ("Labels", {
                "title": _("Labels"),
                "toggle": True,
                "sortable": False}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        labels = label_api.get_obj_labels(obj)
        portal_type = api.get_portal_type(obj)
        pt = api.get_tool("portal_types")
        fti = pt.getTypeInfo(portal_type)
        type_title = fti.Title()

        item["replace"]["Title"] = get_link_for(obj)
        item["Type"] = t(_(type_title))
        item["Labels"] = ", ".join(labels)
        item["replace"]["Labels"] = self.render_labels(labels)

        return item

    @view.memoize
    def _label_colors(self):
        return label_api.get_label_colors()

    def render_labels(self, labels):
        colors = self._label_colors()
        template = ViewPageTemplateFile("templates/object_labels.pt")
        return template(self, labels=labels, colors=colors,
                        chip_style=label_api.chip_style)

    def folderitems(self):
        items = super(LabeledObjectsView, self).folderitems()
        return items
