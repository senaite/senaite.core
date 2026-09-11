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
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_link
from senaite.core.browser.controlpanel.listing import ControlPanelListingView
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.i18n import translate
from senaite.core.permissions import AddAnalysisSpec


class AnalysisSpecsView(ControlPanelListingView):
    """Displays all system's dynamic analysis specifications
    """

    def __init__(self, context, request):
        super(AnalysisSpecsView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG

        self.contentFilter = {
            "portal_type": "AnalysisSpec",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(self.context),
                "depth": 0,
            },
        }

        self.context_actions = {
            _("listing_analysisspec_action_add", default="Add"): {
                "url": "++add++AnalysisSpec",
                "permission": AddAnalysisSpec,
                "icon": "senaite_theme/icon/plus"
            }
        }

        self.icon = api.get_icon("AnalysisSpecs", html_tag=False)

        self.title = translate(_(
            u"listing_analysisspecs_title",
            default=u"Analysis Specifications")
        )
        self.description = self.context.Description()
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _(
                    u"listing_analysisspecs_column_title",
                    default=u"Analysis Specification"
                ),
                "index": "sortable_title"}),
            ("SampleType", {
                "title": _(
                    u"listing_analysisspecs_column_sampletype",
                    default=u"SampleType"
                ),
                "index": "sampletype_title"}),
            ("DynamicSpec", {
                "title": _(
                    u"listing_analysisspecs_column_dynamic_specification",
                    default=u"Dynamic Specification"),
                "sortable": False,
            })
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_analysisspecs_state_active",
                    default=u"Active"
                ),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _(
                    u"listing_analysisspecs_state_inactive",
                    default=u"Inactive"
                ),
                "contentFilter": {"is_active": False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    u"listing_analysisspecs_state_all",
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
        title = obj.Title()
        url = obj.absolute_url()

        item["replace"]["Title"] = get_link(url, value=title)

        sampletype = obj.getSampleType()
        if sampletype:
            title = sampletype.Title()
            url = sampletype.absolute_url()
            item["replace"]["SampleType"] = get_link(url, value=title)

        dynamic_spec = obj.getDynamicAnalysisSpec()
        if dynamic_spec:
            title = dynamic_spec.Title()
            url = api.get_url(dynamic_spec)
            item["replace"]["DynamicSpec"] = get_link(url, value=title)

        return item
