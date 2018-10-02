# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import ICalculations
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from zope.interface.declarations import implements


# TODO: Separate content and view into own modules!


class CalculationsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(CalculationsView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "Calculation",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=Calculation",
                "permission": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Calculations"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/calculation_big.png"
        )
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Calculation"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "Description",
                "toggle": True}),
            ("Formula", {
                "title": _("Formula"),
                "index": "getFormula",
                "toggle": True}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"inactive_state": "active"},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Dormant"),
                "contentFilter": {"inactive_state": "inactive"},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            }
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
        title = obj.Title()
        description = obj.Description()
        url = obj.absolute_url()

        item["replace"]["Title"] = get_link(url, value=title)
        item["Description"] = description
        item["Formula"] = obj.getMinifiedFormula()

        return item


schema = ATFolderSchema.copy()


class Calculations(ATFolder):
    implements(ICalculations)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Calculations, PROJECTNAME)
