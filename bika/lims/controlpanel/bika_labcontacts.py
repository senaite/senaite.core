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
from bika.lims.interfaces import ILabContacts
from bika.lims.utils import get_email_link
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from zope.interface.declarations import implements


# TODO: Separate content and view into own modules!


class LabContactsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(LabContactsView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "LabContact",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=LabContact",
                "permission": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Lab Contacts"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/lab_contact_big.png"
        )

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            # TODO: Better sort by last name (index required!)
            ("Fullname", {
                "title": _("Name"),
                "index": "getFullname"}),
            ("DefaultDepartment", {
                "title": _("Default Department"),
                "toggle": False}),
            ("Departments", {
                "title": _("Departments"),
                "toggle": True}),
            ("BusinessPhone", {
                "title": _("Phone"),
                "toggle": True}),
            ("Fax", {
                "title": _("Fax"),
                "toggle": False}),
            ("MobilePhone", {
                "title": _("Mobile Phone"),
                "toggle": True}),
            ("EmailAddress", {
                "title": _("Email Address"),
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

        fullname = obj.getFullname()
        if fullname:
            item["Fullname"] = fullname
            item["replace"]["Fullname"] = get_link(
                obj.absolute_url(), value=fullname)
        else:
            item["Fullname"] = ""

        default_department = obj.getDefaultDepartment()
        if default_department:
            item["replace"]["DefaultDepartment"] = get_link(
                default_department.absolute_url(),
                value=default_department.Title())

        departments = obj.getDepartments()
        if departments:
            links = map(
                lambda o: get_link(o.absolute_url(),
                                   value=o.Title(),
                                   css_class="link"),
                departments)
            item["replace"]["Departments"] = ", ".join(links)

        email = obj.getEmailAddress()
        if email:
            item["EmailAddress"] = obj.getEmailAddress()
            item["replace"]["EmailAddress"] = get_email_link(
                email, value=email)

        item["BusinessPhone"] = obj.getBusinessPhone()
        item["Fax"] = obj.getBusinessFax()
        item["MobilePhone"] = obj.getMobilePhone()

        return item


schema = ATFolderSchema.copy()


class LabContacts(ATFolder):
    implements(ILabContacts)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(LabContacts, PROJECTNAME)
