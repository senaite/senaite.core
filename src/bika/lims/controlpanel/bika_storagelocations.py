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
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IStorageLocations
from bika.lims.permissions import AddStorageLocation
from bika.lims.utils import get_link
from bika.lims.utils import get_link_for
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from senaite.core.interfaces import IHideActionsMenu
from zope.interface.declarations import implements


class StorageLocationsView(BikaListingView):

    def __init__(self, context, request):
        super(StorageLocationsView, self).__init__(context, request)

        self.catalog = "senaite_catalog_setup"

        self.contentFilter = {
            "portal_type": "StorageLocation",
            "sort_on": "sortable_title",
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=StorageLocation",
                "permission": AddStorageLocation,
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Storage Locations"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/storagelocation_big.png"
        )
        self.description = ""

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Storage Location"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "description",
                "toggle": True}),
            ("SiteTitle", {
                "title": _("Site Title"),
                "toggle": True}),
            ("SiteCode", {
                "title": _("Site Code"),
                "toggle": True}),
            ("LocationTitle", {
                "title": _("Location Title"),
                "toggle": True}),
            ("LocationCode", {
                "title": _("Location Code"),
                "toggle": True}),
            ("ShelfTitle", {
                "title": _("Shelf Title"),
                "toggle": True}),
            ("ShelfCode", {
                "title": _("Shelf Code"),
                "toggle": True}),
            ("Owner", {
                "title": _("Owner"),
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
                "contentFilter": {"is_active": False},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item["Description"] = obj.Description()
        item["replace"]["Title"] = get_link(item["url"], item["Title"])

        item["SiteTitle"] = obj.getSiteTitle()
        item["SiteCode"] = obj.getSiteCode()
        item["LocationTitle"] = obj.getLocationTitle()
        item["LocationCode"] = obj.getLocationCode()
        item["ShelfTitle"] = obj.getShelfTitle()
        item["ShelfCode"] = obj.getShelfCode()

        parent = api.get_parent(obj)
        if IClient.providedBy(parent):
            item["Owner"] = api.get_title(parent)
            item["replace"]["Owner"] = get_link_for(parent)
        else:
            lab = self.context.bika_setup.laboratory
            item["Owner"] = lab.Title()
            item["replace"]["Owner"] = get_link_for(lab)

        return item


schema = ATFolderSchema.copy()


class StorageLocations(ATFolder):
    implements(IStorageLocations, IHideActionsMenu)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(StorageLocations, PROJECTNAME)
