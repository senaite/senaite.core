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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import ISampleTypes
from bika.lims.permissions import AddSampleType
from bika.lims.utils import get_link_for
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from senaite.core.interfaces import IHideActionsMenu
from zope.interface.declarations import implements

# TODO: Separate content and view into own modules!


class SampleTypesView(BikaListingView):

    def __init__(self, context, request):
        super(SampleTypesView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG
        self.contentFilter = {
            "portal_type": "SampleType",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            }
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=SampleType",
                "permission": AddSampleType,
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Sample Types"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/sampletype_big.png"
        )

        self.description = ""

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Sample Type"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "description",
                "toggle": True}),
            ("getHazardous", {
                "title": _("Hazardous"),
                "toggle": True}),
            ("getPrefix", {
                "title": _("Prefix"),
                "toggle": True}),
            ("getMinimumVolume", {
                "title": _("Minimum Volume"),
                "toggle": True}),
            ("RetentionPeriod", {
                "title": _("Retention Period"),
                "toggle": True}),
            ("SampleMatrix", {
                "title": _("SampleMatrix"),
                "toggle": True}),
            ("ContainerType", {
                "title": _("Default Container"),
                "toggle": True}),
            ("SamplePoints", {
                "title": _("Sample Points"),
                "toggle": True}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {'is_active': False},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
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
            hours = retention_period.get("hours", "0")
            minutes = retention_period.get("minutes", "0")
            days = retention_period.get("days", "0")
            item["RetentionPeriod"] = _("hours: {} minutes: {} days: {}"
                                        .format(hours, minutes, days))

        sample_matrix = obj.getSampleMatrix()
        item["replace"]["SampleMatrix"] = get_link_for(sample_matrix)

        container_type = obj.getContainerType()
        item["replace"]["ContainerType"] = get_link_for(container_type)

        # Hazardous
        hazardous = obj.getHazardous()
        item["getHazardous"] = hazardous

        # Prefix
        prefix = obj.getPrefix()
        item["getPrefix"] = prefix

        # Minimum Volume
        vol = obj.getMinimumVolume()
        item["getMinimumVolume"] = vol

        # Hide sample points assigned to this sample type that do not belong
        # to the same container (Client or Setup)
        sample_points = obj.getSamplePoints()
        path = api.get_path(self.context)
        setup = api.get_setup()
        if api.get_parent(self.context) == setup:
            path = api.get_path(setup.bika_samplepoints)

        sample_points = filter(lambda sp: api.get_parent_path(sp) == path,
                               sample_points)

        # Display the links to the sample points
        links = map(get_link_for, sample_points)
        item["replace"]["SamplePoints"] = ", ".join(links)

        return item


schema = ATFolderSchema.copy()


class SampleTypes(ATFolder):
    """Sample Types Folder
    """
    implements(ISampleTypes, IHideActionsMenu)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(SampleTypes, PROJECTNAME)
