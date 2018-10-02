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
from bika.lims.browser.referencesample import ReferenceSamplesView
from bika.lims.controlpanel.bika_instruments import InstrumentsView
from bika.lims.utils import get_link


class SupplierInstrumentsView(InstrumentsView):
    """Supplier Instruments
    """

    def __init__(self, context, request):
        super(SupplierInstrumentsView, self).__init__(context, request)

        portal = api.get_portal()
        portal_url = portal.absolute_url()

        add_url = "{}/{}/{}/createObject?type_name={}".format(
            portal_url, "bika_setup", "bika_instruments", "Instrument")

        self.context_actions = {
            _("Add"): {
                "url": add_url,
                "permisison": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}
        }

    def before_render(self):
        """Before template render hook
        """
        pass

    def isItemAllowed(self, obj):
        supp = obj.getRawSupplier() if obj else None
        return supp == self.context.UID() if supp else False


class SupplierReferenceSamplesView(ReferenceSamplesView):
    """Supplier Reference Samples
    """

    def __init__(self, context, request):
        super(SupplierReferenceSamplesView, self).__init__(context, request)

        self.contentFilter["path"]["query"] = api.get_path(context)

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=ReferenceSample",
                "permission": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        # Remove the Supplier column from the list
        del self.columns["Supplier"]
        for rs in self.review_states:
            rs["columns"] = [col for col in rs["columns"] if col != "Supplier"]


class ContactsView(BikaListingView):
    """Supplier Contacts
    """

    def __init__(self, context, request):
        super(ContactsView, self).__init__(context, request)

        self.catalog = "portal_catalog"

        self.contentFilter = {
            "portal_type": "SupplierContact",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": "/".join(context.getPhysicalPath()),
                "level": 0}
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=SupplierContact",
                "permission": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Contacts"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/contact_big.png"
        )

        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("getFullname", {
                "title": _("FullName")}),
            ("getEmailAddress", {
                "title": _("Email Address")}),
            ("getBusinessPhone", {
                "title": _("Business Phone")}),
            ("getMobilePhone", {
                "title": _("Mobile Phone")}),
            ("getFax", {
                "title": _("Fax")}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """

        name = obj.getFullname()
        url = obj.absolute_url()

        item["replace"]["getFullname"] = get_link(url, value=name)

        return item
