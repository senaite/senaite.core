# -*- coding: utf-8 -*-

import collections
from bika.lims import api
from bika.lims.utils import get_link_for
from senaite.app.listing import ListingView
from bika.lims import senaiteMessageFactory as _


class ClientsGroupsListingView(ListingView):
    """Listing view of Clients Groups
    """

    def __init__(self, context, request):
        super(ClientsGroupsListingView, self).__init__(context, request)

        self.catalog = "portal_catalog"

        self.contentFilter = {
            "portal_type": "ClientsGroup",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {
            _("Add"): {
                "url": "++add++ClientsGroup",
                "permission": "Add portal content",
                "icon": "add.png"}
            }

        self.show_select_column = True

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Title"),
                "index": "sortable_title"
            }),
            ("Description", {
                "title": _("Description"),
                "index": "Description"
            }),
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
        super(ClientsGroupsListingView, self).update()

    def before_render(self):
        """Before template render hook
        """
        super(ClientsGroupsListingView, self).before_render()

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        obj = api.get_object(obj)
        item["replace"]["Title"] = get_link_for(obj)
        return item
