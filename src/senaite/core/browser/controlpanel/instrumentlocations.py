# -*- coding: utf-8 -*-

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.permissions import AddInstrumentLocation
from bika.lims.utils import get_link
from senaite.app.listing import ListingView


class InstrumentLocationsView(ListingView):
    """Displays all available instrument locations in a table
    """

    def __init__(self, context, request):
        super(InstrumentLocationsView, self).__init__(context, request)

        self.contentFilter = {
            "portal_type": "InstrumentLocation",
            "sort_on": "sortable_title",
        }

        self.context_actions = {
            _("Add"): {
                "url": "++add++InstrumentLocation",
                "permission": AddInstrumentLocation,
                "icon": "++resource++bika.lims.images/add.png",
            }}

        self.title = self.context.translate(_("Instrument Locations"))
        self.icon = "++resource++bika.lims.images/instrumenttype_big.png"
        self.description = ""

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Location"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "Description",
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
                "columns": self.columns.keys(),
            }, {
                "id": "all",
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
        obj = api.get_object(obj)
        title = obj.Title()
        description = obj.Description()
        url = obj.absolute_url()

        item["replace"]["Title"] = get_link(url, value=title)
        item["Description"] = description

        return item
