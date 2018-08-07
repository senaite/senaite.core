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
from bika.lims.interfaces import IInstruments
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.utils import get_link
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from zope.interface.declarations import implements


# TODO: Separate content and view into own modules!


class InstrumentsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentsView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "Instrument",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=Instrument",
                "permisison": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Instruments"))
        self.description = ""
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/instrument_big.png"
        )

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Instrument"),
                "index": "sortable_title"}),
            ("Type", {
                "title": _("Type"),
                "index": "getInstrumentTypeName",
                "toggle": True,
                "sortable": True}),
            ("Brand", {
                "title": _("Brand"),
                "sortable": False,
                "toggle": True}),
            ("Model", {
                "title": _("Model"),
                "index": "getModel",
                "toggle": True}),
            ("ExpiryDate", {
                "title": _("Expiry Date"),
                "sortable": False,
                "toggle": True}),
            ("WeeksToExpire", {
                "title": _("Weeks To Expire"),
                "sortable": False,
                "toggle": False}),
            ("Methods", {
                "title": _("Methods"),
                "sortable": False,
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
        # Don't allow any context actions on the Instruments folder
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
        url = obj.absolute_url()

        item["Title"] = title
        item["replace"]["Title"] = get_link(url, value=title)

        instrument_type = obj.getInstrumentType()
        if instrument_type:
            url = instrument_type.absolute_url()
            title = instrument_type.Title()
            item["Type"] = instrument_type.Title()
            item["replace"]["Type"] = get_link(url, value=title)
        else:
            item["Type"] = ""

        instrument_brand = obj.getManufacturer()
        if instrument_brand:
            url = instrument_brand.absolute_url()
            title = instrument_brand.Title()
            item["Brand"] = instrument_brand.Title()
            item["replace"]["Brand"] = get_link(url, value=title)
        else:
            item["Brand"] = ""

        instrument_model = obj.getModel()
        if instrument_model:
            item["Model"] = instrument_model
        else:
            item["Model"] = ""

        expiry_date = obj.getCertificateExpireDate()
        if expiry_date is None:
            item["ExpiryDate"] = _("No date set")
        else:

            item["ExpiryDate"] = expiry_date.asdatetime().strftime(
                self.date_format_short)

        if obj.isOutOfDate():
            item["WeeksToExpire"] = _("Out of date")
        else:
            weeks, days = obj.getWeeksToExpire()
            weeks_to_expire = _("{} weeks and {} day(s)".format(
                str(weeks), str(days)))
            item['WeeksToExpire'] = weeks_to_expire

        methods = obj.getMethods()
        if methods:
            links = map(
                lambda m: get_link(m.absolute_url(),
                                   value=m.Title(),
                                   css_class="link"),
                methods)
            item["replace"]["Methods"] = ", ".join(links)

        return item


schema = ATFolderSchema.copy()


class Instruments(ATFolder):
    """Instruments Folder
    """
    implements(IInstruments)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(Instruments, PROJECTNAME)
