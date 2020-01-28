# -*- coding: utf-8 -*-

import collections

from bika.lims import _
from bika.lims import api
from senaite.core.listing.view import ListingView


class DynamicAnalysisSpecView(ListingView):
    """A listing view that shows the contents of the Excel
    """
    def __init__(self, context, request):
        super(DynamicAnalysisSpecView, self).__init__(context, request)

        self.pagesize = 50
        self.context_actions = {}
        self.title = api.get_title(self.context)
        self.description = api.get_description(self.context)
        self.show_search = False
        self.show_column_toggles = False

        if self.context.specs_file:
            filename = self.context.specs_file.filename
            self.description = _("Contents of the file {}".format(filename))

        self.specs = self.context.get_specs()
        self.total = len(self.specs)

        self.columns = collections.OrderedDict()
        for title in self.context.get_header():
            self.columns[title] = {
                "title": title,
                "toggle": True}

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys()
            }
        ]

    def update(self):
        super(DynamicAnalysisSpecView, self).update()

    def before_render(self):
        super(DynamicAnalysisSpecView, self).before_render()

    def make_empty_item(self, **kw):
        """Create a new empty item
        """
        item = {
            "uid": None,
            "before": {},
            "after": {},
            "replace": {},
            "allow_edit": [],
            "disabled": False,
            "state_class": "state-active",
        }
        item.update(**kw)
        return item

    def folderitems(self):
        items = []
        for record in self.specs:
            items.append(self.make_empty_item(**record))
        return items
