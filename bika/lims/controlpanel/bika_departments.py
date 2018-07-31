# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IDepartments
from bika.lims.utils import get_email_link
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.content import schemata
from zope.interface.declarations import implements


# TODO: Separate content and view into own modules!


class DepartmentsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(DepartmentsView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"

        self.contentFilter = {
            "portal_type": "Department",
            "sort_order": "ascending",
            "sort_on": "sortable_title"
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=Department",
                "permission": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Lab Departments"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/department_big.png"
        )

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Department"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "Description",
                "toggle": True}),
            ("Manager", {
                "title": _("Manager"),
                "index": "getManagerName",
                "toggle": True}),
            ("ManagerPhone", {
                "title": _("Manager Phone"),
                "index": "getManagerPhone",
                "toggle": True}),
            ("ManagerEmail", {
                "title": _("Manager Email"),
                "index": "getManagerEmail",
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
        title = obj.Title()
        description = obj.Description()
        url = obj.absolute_url()

        item["replace"]["Title"] = get_link(url, value=title)
        item["Description"] = description

        manager = obj.getManager()
        manager_name = obj.getManagerName()
        manager_phone = obj.getManagerPhone()
        manager_email = obj.getManagerEmail()

        if manager:
            item["Manager"] = manager_name
            item["replace"]["Manager"] = get_link(
                manager.absolute_url(), manager_name)
        else:
            item["Manager"] = ""

        if manager_email:
            item["ManagerEmail"] = manager_email
            item["replace"]["ManagerEmail"] = get_email_link(
                manager_email, value=manager_email)
        else:
            item["ManagerEmail"] = ""

        item["ManagerPhone"] = manager_phone

        return item


schema = ATFolderSchema.copy()


class Departments(ATFolder):
    implements(IDepartments)
    displayContentsTab = False
    schema = schema

    def getContacts(self, active_only=True):
        catalog = api.get_tool("bika_setup_catalog")
        query = {
            "portal_type": "LabContact",
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        }
        results = catalog(query)

        # XXX  Better directly filter in the catalog query as soon as we have
        #      the active/inactive state in the primary workflow
        if active_only:
            results = filter(api.is_active, results)

        pairs = map(
            lambda brain: (brain.UID, brain.Title), results)

        return DisplayList(pairs)


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Departments, PROJECTNAME)
