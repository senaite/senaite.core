# -*- coding: utf-8 -*-

from collections import OrderedDict
from itertools import chain

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.worksheet.views import AnalysesTransposedView
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.utils import get_link
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger
from senaite.core.i18n import translate as t
from six.moves.urllib.parse import parse_qs


class MultiResultsTransposedView(AnalysesTransposedView):
    """Transposed multi results view
    """
    template = ViewPageTemplateFile("templates/multi_results.pt")

    def __init__(self, context, request):
        super(MultiResultsTransposedView, self).__init__(context, request)

        self.allow_edit = True
        self.expand_all_categories = False
        self.show_categories = False
        self.show_column_toggles = False
        self.show_search = False
        self.show_select_column = True

        self.transposed = True
        self.classic_url = "{}/multi_results_classic?uids={}".format(
            self.context.absolute_url(), self.request.form.get("uids"))

        self.title = _("Multi Results")
        self.description = _("")

        self.headers = OrderedDict()
        self.services = OrderedDict()

        self.columns = OrderedDict((
            ("column_key", {
                "title": "",
                "sortable": False}),
            ("Result", {
                "title": _("Result"),
                "ajax": True,
                "sortable": False}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "custom_transitions": [],
                "columns": self.columns.keys(),
            },
        ]

    def make_empty_folderitem(self, **kw):
        """Create a new empty item
        """
        item = AnalysesView.make_empty_folderitem(self, **kw)
        item["transposed_keys"] = []
        item.update(**kw)
        return item

    def transpose_item(self, item, pos):
        """Transpose the folderitem
        """
        obj = api.get_object(item["obj"])
        service = item["Service"]
        keyword = obj.getKeyword()
        item["Pos"] = pos

        # skip retracted analyses
        review_state = item["review_state"]
        if review_state in ["retracted"]:
            return item

        # show only retests
        if obj.getRetest():
            return item

        # remember the column headers of the first row
        if "Pos" not in self.headers:
            self.headers["Pos"] = self.make_empty_folderitem(
                column_key=t(_("Position")), item_key="Pos")

        # remember the services, e.g. Calcium, Magnesium, Total Hardness etc.
        if keyword not in self.services:
            transposed_item = self.make_empty_folderitem(
                column_key=keyword, item_key="Result")
            # Append info link after the service
            transposed_item["after"]["column_key"] = get_link(
                "analysisservice_info?service_uid={}&analysis_uid={}"
                .format(item["service_uid"], item["uid"]),
                value="<i class='fas fa-info-circle'></i>",
                css_class="overlay_panel")
            transposed_item["replace"]["column_key"] = service
            self.services[keyword] = transposed_item

        # append all regular items that belong to this service
        if pos not in self.services[keyword]:
            header_item = self.make_empty_folderitem()
            # Add the item with the Pos header
            header_item["replace"]["Pos"] = self.get_slot_header(item)
            # Append to header
            self.headers["Pos"][pos] = header_item
            # Add the item below its position
            self.services[keyword][pos] = item
            # Track the new transposed key for this item
            self.services[keyword]["transposed_keys"].append(pos)

        return item

    def folderitems(self):
        """Prepare transposed analyses folderitems

        NOTE: This method is called by a separate Ajax request, which creates
              a new view instance!

              Therefore, we do all dynamic modifications to the columns etc.
              right here to avoid expensive operations called multiple times!
        """
        samples = self.get_samples()

        for num, sample in enumerate(samples):
            slot = str(num + 1)
            # Add a new column for the sample
            self.columns[slot] = {
                "title": "",
                "type": "transposed",
                "sortable": False,
            }
            for item in self.get_sample_folderitems(sample):
                transposed = self.transpose_item(item, slot)

        # show service and sample columns
        slots = [str(i + 1) for i in range(len(samples))]
        self.review_states[0]["columns"] = ["column_key"] + slots

        # transposed rows holder
        transposed = OrderedDict()

        # HTML slot headers
        transposed.update(self.headers)

        # collected services (Iron, Copper, Calcium...)
        services = OrderedDict(reversed(self.services.items()))
        transposed.update(services)

        # listing fixtures
        self.total = len(transposed.keys())

        # return the transposed rows
        return transposed.values()

    def get_sample_folderitems(self, sample):
        """Get the folderitems for the given sample
        """
        view = AnalysesView(sample, self.request)
        view.contentFilter["getAncestorsUIDs"] = [api.get_uid(sample)]
        return view.folderitems()

    def get_analyses(self, full_objects=False):
        """Returns all sample analyses
        """
        analyses = map(lambda s: s.getAnalyses(full_objects=full_objects),
                       self.get_samples())
        # return a flat list of analyses
        return list(chain(*analyses))

    def get_samples(self):
        """Extract the samples from the request UIDs

        This might be either a samples container or a sample context
        """

        # fetch objects from request
        objs = self.get_objects_from_request()

        samples = []

        for obj in objs:
            # when coming from the samples listing
            if IAnalysisRequest.providedBy(obj):
                samples.append(obj)

        # when coming from the WF menu inside a sample
        if IAnalysisRequest.providedBy(self.context):
            samples.append(self.context)

        return self.uniquify_items(samples)

    def uniquify_items(self, items):
        """Uniquify the items with sort order
        """
        unique = []
        for item in items:
            if item in unique:
                continue
            unique.append(item)
        return unique

    def get_objects_from_request(self):
        """Returns a list of objects coming from the "uids" request parameter
        """
        unique_uids = self.get_uids_from_request()
        return filter(None, map(self.get_object_by_uid, unique_uids))

    def get_uids_from_request(self):
        """Return a list of uids from the request
        """
        qs = self.request.get_header("query_string")
        params = dict(parse_qs(qs))
        uids = params.get("uids", [""])[0]
        if api.is_string(uids):
            uids = uids.split(",")
        unique_uids = OrderedDict().fromkeys(uids).keys()
        return filter(api.is_uid, unique_uids)

    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID #{} !!")
        return obj
