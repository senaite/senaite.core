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
from bika.lims.interfaces import IReferenceDefinitions
from bika.lims.permissions import AddReferenceDefinition
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from bika.lims.utils import t
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import registerType
from zope.interface.declarations import implements


class ReferenceDefinitionsView(BikaListingView):
    """Listing view for all Methods
    """

    def __init__(self, context, request):
        super(ReferenceDefinitionsView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"

        self.contentFilter = {
            "portal_type": "ReferenceDefinition",
            "sort_on": "sortable_title",
            "sort_order": "ascending"

        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=ReferenceDefinition",
                "permission": AddReferenceDefinition,
                "icon": "++resource++bika.lims.images/add.png"}}

        self.title = self.context.translate(_("Reference Definitions"))
        self.description = ""
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/referencedefinition_big.png")

        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Title"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "description",
                "toggle": True}),
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
                "contentFilter": {"is_active": False},
                "columns": self.columns.keys(),
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
        """Applies new properties to the item (Client) that is currently being
        rendered as a row in the list

        :param obj: client to be rendered as a row in the list
        :param item: dict representation of the client, suitable for the list
        :param index: current position of the item within the list
        :type obj: ATContentType/DexterityContentType
        :type item: dict
        :type index: int
        :return: the dict representation of the item
        :rtype: dict
        """

        url = obj.absolute_url()
        title = obj.Title()

        item['Description'] = obj.Description()
        item["replace"]["Title"] = get_link(url, value=title)

        # Icons
        after_icons = ""
        if obj.getBlank():
            after_icons += get_image(
                "blank.png", title=t(_("Blank")))
        if obj.getHazardous():
            after_icons += get_image(
                "hazardous.png", title=t(_("Hazardous")))
        if after_icons:
            item["after"]["ID"] = after_icons

        return item


schema = ATFolderSchema.copy()


class ReferenceDefinitions(ATFolder):
    """Reference definition content
    """
    implements(IReferenceDefinitions)

    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(ReferenceDefinitions, PROJECTNAME)
