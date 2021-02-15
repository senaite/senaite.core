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

from bika.lims import _
from bika.lims import api
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.permissions import AddAnalysisSpec
from bika.lims.utils import get_link
from plone.dexterity.content import Container
from plone.supermodel import model
from senaite.core.listing import ListingView
from zope import schema
from zope.interface import implements


class IDynamicAnalysisSpecs(model.Schema):
    """Dynamic Analysis Specifications
    """
    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Title of the Folder"),
        required=True)


class DynamicAnalysisSpecsView(ListingView):
    """Displays all system's dynamic analysis specifications
    """

    def __init__(self, context, request):
        super(DynamicAnalysisSpecsView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG

        self.contentFilter = {
            "portal_type": "DynamicAnalysisSpec",
            "sort_on": "created",
            "sort_order": "descending",
        }

        self.context_actions = {
            _("Add"): {
                "url": "++add++DynamicAnalysisSpec",
                "permission": AddAnalysisSpec,
                "icon": "++resource++bika.lims.images/add.png"}
            }

        self.icon = "{}/{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images",
            "analysisspec_big.png"
        )

        self.title = self.context.Title()
        self.description = self.context.Description()
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Title"),
                "replace_url": "getURL",
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "Description"}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {'is_active': False},
                "transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def update(self):
        """Update hook
        """
        super(DynamicAnalysisSpecsView, self).update()

    def before_render(self):
        """Before template render hook
        """
        super(DynamicAnalysisSpecsView, self).before_render()
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
        item["replace"]["Title"] = get_link(
            api.get_url(obj), value=api.get_title(obj))
        return item


class DynamicAnalysisSpecs(Container):
    """Dynamic Analysis Specifications Folder
    """
    implements(IDynamicAnalysisSpecs)
