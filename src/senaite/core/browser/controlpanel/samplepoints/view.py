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
from senaite.app.listing import ListingView
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.i18n import translate
from senaite.core.permissions import AddSamplePoint


class SamplePointsView(ListingView):

    def __init__(self, context, request):
        super(SamplePointsView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG
        self.show_select_column = True

        self.contentFilter = {
            "portal_type": "SamplePoint",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(context),
                "level": 0,
            }
        }

        self.context_actions = {
            _(u"listing_samplepoints_action_add", default=u"Add"): {
                "url": "++add++SamplePoint",
                "permission": AddSamplePoint,
                "icon": "senaite_theme/icon/plus"
            }
        }

        self.title = translate(_(
            u"listing_samplepoints_title",
            default=u"Sample Points")
        )
        self.icon = api.get_icon("SamplePoints", html_tag=False)

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _(
                    u"listing_samplepoints_column_title",
                    default=u"Sample Point"
                ),
                "index": "sortable_title"
            }),
            ("Description", {
                "title": _(
                    u"listing_samplepoints_column_description",
                    default=u"Description"
                ),
                "toggle": True
            }),
            ("SampleTypes", {
                "title": _(
                    u"listing_samplepoints_column_sampletypes",
                    default=u"Sample Types",
                ),
                "index": "sampletype_title",
                "sortable": True,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_samplepoints_state_active",
                    default=u"Active"
                ),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _(
                    u"listing_samplepoints_state_inactive",
                    default=u"Inactive"
                ),
                "contentFilter": {"is_active": False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    u"listing_samplepoints_state_all",
                    default=u"All"
                ),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item["replace"]["Title"] = get_link_for(obj)
        item["Description"] = obj.Description()

        sample_types = obj.getSampleTypes()
        titles = map(api.get_title, sample_types)
        links = map(get_link_for, sample_types)
        item["SampleTypes"] = ", ".join(titles)
        item["replace"]["SampleTypes"] = ", ".join(links)
        return item
