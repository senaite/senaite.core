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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IWorksheetTemplates
from bika.lims.permissions import AddWorksheetTemplate
from bika.lims.utils import get_link
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from zope.interface.declarations import implements


class WorksheetTemplatesView(BikaListingView):
    """Listing View for Worksheet Templates
    """

    def __init__(self, context, request):
        super(WorksheetTemplatesView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"

        self.contentFilter = {
            "portal_type": "WorksheetTemplate",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {
            _("Add"):
            {
                "url": "createObject?type_name=WorksheetTemplate",
                "permission": AddWorksheetTemplate,
                "icon": "++resource++bika.lims.images/add.png"
            }
        }

        self.title = self.context.translate(_("Worksheet Templates"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/worksheettemplate_big.png"
        )

        self.show_select_row = False
        self.show_select_column = True

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Title"),
                "index": "sortable_title",
            }),
            ("Description", {
                "title": _("Description"),
                "index": "description",
                "toggle": True,
            }),
            ("Method", {
                "title": _("Method"),
                "toggle": True}),
            ("Instrument", {
                "title": _("Instrument"),
                "index": "instrument_title",
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
                "columns": self.columns.keys()
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        obj = api.get_object(obj)
        item["Description"] = obj.Description()
        item["replace"]["Title"] = get_link(item["url"], item["Title"])

        instrument = obj.getInstrument()
        if instrument:
            instrument_url = api.get_url(instrument)
            instrument_title = api.get_title(instrument)
            item["Instrument"] = instrument_title
            item["replace"]["Instrument"] = get_link(
                instrument_url, value=instrument_title)

        # Method
        method_uid = obj.getMethodUID()
        if method_uid:
            method = api.get_object_by_uid(method_uid)
            method_url = api.get_url(method)
            method_title = api.get_title(method)
            item["Method"] = method_title
            item["replace"]["Method"] = get_link(
                method_url, value=method_title)

        return item


schema = ATFolderSchema.copy()


class WorksheetTemplates(ATFolder):
    implements(IWorksheetTemplates)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(WorksheetTemplates, PROJECTNAME)
