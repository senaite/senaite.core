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
from cgi import escape as html_escape

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from senaite.core.api import label as label_api
from senaite.core.browser.controlpanel.listing import ControlPanelListingView
from senaite.core.catalog import SETUP_CATALOG


class LabelsView(ControlPanelListingView):
    """Displays all available labels
    """

    def __init__(self, context, request):
        super(LabelsView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG

        self.contentFilter = {
            "portal_type": "Label",
            "sort_on": "sortable_title",
        }

        self.context_actions = {
            _("Add"): {
                "url": "++add++Label",
                "icon": "++resource++bika.lims.images/add.png",
            }}

        t = self.context.translate
        self.title = t(_("Labels"))
        self.description = t(_("Add default selectable labels"))

        self.show_select_column = True
        self.show_all = False

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Title"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "toggle": True,
            }),
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
        # Always wake the object: we need Title / URL / Description
        # anyway, so the brain-metadata shortcut would not save a wake.
        obj = api.get_object(obj)
        color = getattr(obj, "color", u"") or u""
        if not label_api.is_safe_color(color):
            color = u""

        title = api.safe_unicode(api.get_title(obj))
        url = api.safe_unicode(api.get_url(obj))
        style = label_api.chip_style(color)
        style_attr = u' style="{}"'.format(style) if style else u""

        item["replace"]["Title"] = (
            u'<a class="sample-label" href="{url}"{style}>'
            u'<span class="sample-label-text">{title}</span></a>'
        ).format(
            url=html_escape(url, quote=True),
            style=style_attr,
            title=html_escape(title),
        )
        item["Description"] = api.get_description(obj)
        return item

    def folderitems(self):
        items = super(LabelsView, self).folderitems()
        return items
