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
from bika.lims.interfaces import ISamplePoints
from bika.lims.permissions import AddSamplePoint
from bika.lims.utils import get_link_for
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from senaite.core.interfaces import IHideActionsMenu
from zope.interface.declarations import implements

# TODO: Separate content and view into own modules!


class SamplePointsView(BikaListingView):

    def __init__(self, context, request):
        super(SamplePointsView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG
        self.contentFilter = {
            "portal_type": "SamplePoint",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            }
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=SamplePoint",
                "permission": AddSamplePoint,
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Sample Points"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/samplepoint_big.png"
        )

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Sample Point"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "Description",
                "toggle": True}),
            ("getComposite", {
                "title": _("Composite"),
                "sortable": False,
                "toggle": False}),
            ("SampleTypes", {
                "title": _("Sample Types"),
                "index": "sampletype_title",
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

        sample_types = obj.getSampleTypes()
        links = map(get_link_for, sample_types)
        item["replace"]["SampleTypes"] = ", ".join(links)

        return item


schema = ATFolderSchema.copy()


class SamplePoints(ATFolder):
    implements(ISamplePoints, IHideActionsMenu)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(SamplePoints, PROJECTNAME)
