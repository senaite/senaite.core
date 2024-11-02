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
from senaite.core.permissions import AddSampleType


class SampleTypesView(ListingView):

    def __init__(self, context, request):
        super(SampleTypesView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG
        self.show_select_column = True

        self.contentFilter = {
            "portal_type": "SampleType",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(context),
                "depth": 1,
            }
        }

        self.context_actions = {
            _(u"listing_sampletypes_action_add", default=u"Add"): {
                "url": "++add++SampleType",
                "permission": AddSampleType,
                "icon": "senaite_theme/icon/plus"}
        }

        self.title = translate(_(
            u"listing_sampletypes_title",
            default=u"Sample Types")
        )
        self.icon = api.get_icon("SampleTypes", html_tag=False)

        self.columns = collections.OrderedDict((
            ("Title",  {
                "title": _(
                    u"listing_sampletypes_column_title",
                    default=u"Sample Type"
                ),
                "index": "sortable_title"}),
            ("Description", {
                "title": _(
                    u"listing_sampletypes_column_description",
                    default=u"Description"
                ),
                "index": "description",
                "toggle": True}),
            ("hazardous", {
                "title": _(
                    u"listing_sampletypes_column_hazardous",
                    default=u"Hazardous"
                ),
                "toggle": True}),
            ("prefix", {
                "title": _(
                    u"listing_sampletypes_column_prefix",
                    default=u"Prefix"
                ),
                "toggle": True}),
            ("min_volume", {
                "title": _(
                    u"listing_sampletypes_column_min_vol",
                    default=u"Minimum Volume"
                ),
                "toggle": True}),
            ("retention_period", {
                "title": _(
                    u"listing_sampletypes_column_retention_period",
                    default=u"Retention Period"
                ),
                "toggle": True}),
            ("samplematrix", {
                "title": _(
                    u"listing_sampletypes_column_sample_matrix",
                    default=u"SampleMatrix"
                ),
                "toggle": True}),
            ("containertype", {
                "title": _(
                    u"listing_sampletypes_column_default_container",
                    default=u"Default Container"
                ),
                "toggle": True}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title":  _(
                    u"listing_sampletypes_state_active",
                    default=u"Active"
                ),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _(
                    u"listing_sampletypes_state_inactive",
                    default=u"Inactive"
                ),
                "contentFilter": {'is_active': False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    u"listing_sampletypes_state_all",
                    default=u"All"
                ),
                "contentFilter": {},
                "columns": self.columns.keys(),
            }
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

        retention_period = obj.getRetentionPeriod()
        if retention_period:
            days = retention_period.get("days", "0")
            hours = retention_period.get("hours", "0")
            minutes = retention_period.get("minutes", "0")
            item["retention_period"] = \
                "days: {} hours: {} minutes: {}".format(days, hours, minutes)

        sample_matrix = obj.getSampleMatrix()
        item["replace"]["samplematrix"] = get_link_for(sample_matrix)

        container_type = obj.getContainerType()
        item["replace"]["containertype"] = get_link_for(container_type)

        # Hazardous
        hazardous = obj.getHazardous()
        item["hazardous"] = hazardous

        # Prefix
        prefix = obj.getPrefix()
        item["prefix"] = prefix

        # Minimum Volume
        vol = obj.getMinimumVolume()
        item["min_volume"] = vol

        return item
