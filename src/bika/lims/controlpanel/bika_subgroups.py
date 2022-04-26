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

from AccessControl.SecurityInfo import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import ISubGroups
from bika.lims.permissions import AddSubGroup
from bika.lims.utils import get_link
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from senaite.core.interfaces import IHideActionsMenu
from zope.interface.declarations import implements


class SubGroupsView(BikaListingView):

    def __init__(self, context, request):
        super(SubGroupsView, self).__init__(context, request)

        self.catalog = "senaite_catalog_setup"

        self.contentFilter = {
            "portal_type": "SubGroup",
            "sort_on": "sortable_title",
        }
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=SubGroup",
                "permission": AddSubGroup,
                "icon": "++resource++bika.lims.images/add.png"
            }
        }

        self.title = self.context.translate(_("Sub-groups"))
        self.description = ""
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/batch_big.png"
        )

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Attachment Type"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "Description",
                "toggle": True,
            }),
            ("SortKey", {
                "title": _("Sort Key"),
                "toggle": True,
            }),
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
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item["Description"] = obj.Description()
        item["replace"]["Title"] = get_link(item["url"], item["Title"])
        item["SortKey"] = obj.getSortKey()
        return item


schema = ATFolderSchema.copy()


class SubGroups(ATFolder):
    implements(ISubGroups, IHideActionsMenu)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(SubGroups, PROJECTNAME)
