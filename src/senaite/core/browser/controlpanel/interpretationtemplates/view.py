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
from senaite.core.catalog import SETUP_CATALOG
from senaite.app.listing import ListingView
from plone.app.textfield import RichTextValue


class InterpretationTemplatesView(ListingView):
    """Results Interpretation Templates listing view
    """

    def __init__(self, context, request):
        super(InterpretationTemplatesView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG

        self.contentFilter = {
            "portal_type": "InterpretationTemplate",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            },
        }

        self.context_actions = {
            _("listing_interpretationtemplates_action_add", default="Add"): {
                "url": "++add++InterpretationTemplate",
                "icon": "senaite_theme/icon/plus"
            }
        }

        self.title = translate(_(
            "listing_interpretationtemplates_title",
            default="Interpretation Templates")
        )
        self.icon = api.get_icon("InterpretationTemplates",
                                 html_tag=False)
        self.show_select_column = True

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _(
                    u"listing_interpretationtemplates_column_title",
                    default=u"Title"
                ),
                "index": "sortable_title",
            }),
            ("Description", {
                "title": _(
                    u"listing_interpretationtemplates_column_description",
                    default=u"Description"
                ),
            }),
            ("SampleTypes", {
                "title": _(
                    u"listing_interpretationtemplates_column_sampletypes",
                    default=u"Sample Types"
                ),
                "sortable": False,
            }),
            ("Text", {
                "title": _(
                    u"listing_interpretationtemplates_column_text",
                    default=u"Text"
                ),
                "sortable": False,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_interpretationtemplates_state_active",
                    default=u"Active"
                ),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _(
                    u"listing_interpretationtemplates_state_inactive",
                    default=u"Inactive"
                ),
                "contentFilter": {'is_active': False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    u"listing_interpretationtemplates_state_all",
                    default=u"All"
                ),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def update(self):
        """Update hook
        """
        super(InterpretationTemplatesView, self).update()

    def before_render(self):
        """Before template render hook
        """
        super(InterpretationTemplatesView, self).before_render()

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
        item["Description"] = api.get_description(obj)

        # List all linked sampletypes
        sampletypes = obj.getSampleTypes()
        if sampletypes:
            titles = map(api.get_title, sampletypes)
            item["SampleTypes"] = ", ".join(titles)
            item["replace"]["SampleTypes"] = ", ".join(
                map(get_link_for, sampletypes))

        text = obj.text
        if isinstance(text, RichTextValue):
            # convert output to plain text
            text._outputMimeType = "text/plain"
            text = text.output
        item["Text"] = text

        return item
