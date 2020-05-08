# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections
from datetime import datetime

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.chart.analyses import EvolutionChart
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from bika.lims.utils import t
from plone.app.layout.globals.interfaces import IViewView
from plone.memoize import view
from Products.ATContentTypes.utils import DT2dt
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class ViewView(BrowserView):
    """Reference Sample View
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/referencesample_view.pt")

    def __init__(self, context, request):
        super(ViewView, self).__init__(context, request)

        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/referencesample_big.png")

    def __call__(self):
        self.results = {}  # {category_title: listofdicts}
        for r in self.context.getReferenceResults():
            service = api.get_object_by_uid(r["uid"])
            cat = service.getCategoryTitle()
            if cat not in self.results:
                self.results[cat] = []
            r["service"] = service
            self.results[cat].append(r)
        self.categories = self.results.keys()
        self.categories.sort()
        return self.template()


class ReferenceAnalysesViewView(BrowserView):
    """ View of Reference Analyses linked to the Reference Sample.
    """

    implements(IViewView)
    template = ViewPageTemplateFile(
        "templates/referencesample_analyses.pt")

    def __init__(self, context, request):
        super(ReferenceAnalysesViewView, self).__init__(context, request)

        self.title = self.context.translate(_("Reference Analyses"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/referencesample_big.png")

    def __call__(self):
        return self.template()

    def get_analyses_table(self):
        """ Returns the table of Reference Analyses
        """
        return self.get_analyses_view().contents_table()

    def get_analyses_table_view(self):
        view_name = "table_referenceanalyses"
        view = api.get_view(
            view_name, context=self.context, request=self.request)
        # Call listing hooks
        view.update()
        view.before_render()

        # TODO Refactor QC Charts as React Components
        # The current QC Chart is rendered by looking at the value from a
        # hidden input with id "graphdata", that is rendered below the contents
        # listing (see referenceanalyses.pt).
        # The value is a json, is built by folderitem function and is returned
        # by self.chart.get_json(). This function is called directly by the
        # template on render, but the template itself does not directly render
        # the contents listing, but is done asyncronously.
        # Hence the function at this point returns an empty dictionary because
        # folderitems hasn't been called yet. As a result, the chart appears
        # empty. Here, we force folderitems function to be called in order to
        # ensure the graphdata is filled before the template is rendered.
        view.get_folderitems()
        return view


class ReferenceAnalysesView(AnalysesView):
    """Reference Analyses on this sample
    """

    def __init__(self, context, request):
        super(ReferenceAnalysesView, self).__init__(context, request)

        self.form_id = "{}_qcanalyses".format(api.get_uid(context))
        self.allow_edit = False
        self.show_select_column = False
        self.show_search = False
        self.omit_form = True
        self.show_search = False

        self.contentFilter = {
            "portal_type": "ReferenceAnalysis",
            "path": {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0}
        }

        self.columns = collections.OrderedDict((
            ("id", {
                "title": _("ID"),
                "sortable": False,
                "toggle": False}),
            ("getReferenceAnalysesGroupID", {
                "title": _("QC Sample ID"),
                "sortable": False,
                "toggle": True}),
            ("Category", {
                "title": _("Category"),
                "sortable": False,
                "toggle": True}),
            ("Service", {
                "title": _("Service"),
                "sortable": False,
                "toggle": True}),
            ("Worksheet", {
                "title": _("Worksheet"),
                "sortable": False,
                "toggle": True}),
            ("Method", {
                "title": _("Method"),
                "sortable": False,
                "toggle": True}),
            ("Instrument", {
                "title": _("Instrument"),
                "sortable": False,
                "toggle": True}),
            ("Result", {
                "title": _("Result"),
                "sortable": False,
                "toggle": True}),
            ("CaptureDate", {
                "title": _("Captured"),
                "sortable": False,
                "toggle": True}),
            ("Uncertainty", {
                "title": _("+-"),
                "sortable": False,
                "toggle": True}),
            ("DueDate", {
                "title": _("Due Date"),
                "sortable": False,
                "toggle": True}),
            ("retested", {
                "title": _("Retested"),
                "sortable": False,
                "type": "boolean",
                "toggle": True}),
            ("state_title", {
                "title": _("State"),
                "sortable": False,
                "toggle": True}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "transitions": [],
                "columns": self.columns.keys()
            },
        ]
        self.chart = EvolutionChart()

    def is_analysis_edition_allowed(self, analysis_brain):
        """see AnalysesView.is_analysis_edition_allowed
        """
        return False

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        item = super(ReferenceAnalysesView, self).folderitem(obj, item, index)

        if not item:
            return None
        item["Category"] = obj.getCategoryTitle
        ref_analysis = api.get_object(obj)
        ws = ref_analysis.getWorksheet()
        if not ws:
            logger.warn(
                "No Worksheet found for ReferenceAnalysis {}"
                .format(obj.getId))
        else:
            item["Worksheet"] = ws.Title()
            anchor = "<a href='%s'>%s</a>" % (ws.absolute_url(), ws.Title())
            item["replace"]["Worksheet"] = anchor

        # Add the analysis to the QC Chart
        self.chart.add_analysis(obj)
        return item


class ReferenceResultsView(BikaListingView):
    """Listing of all reference results
    """

    def __init__(self, context, request):
        super(ReferenceResultsView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "AnalysisService",
            "UID": self.get_reference_results().keys(),
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        self.context_actions = {}
        self.title = self.context.translate(_("Reference Values"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/referencesample_big.png"
        )

        self.show_select_row = False
        self.show_workflow_action_buttons = False
        self.show_select_column = False
        self.pagesize = 999999
        self.show_search = False

        # Categories
        self.categories = []
        if self.show_categories_enabled():
            self.show_categories = True
            self.expand_all_categories = True

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Analysis Service"),
                "sortable": False}),
            ("result", {
                "title": _("Expected Result"),
                "sortable": False}),
            ("error", {
                "title": _("Permitted Error %"),
                "sortable": False}),
            ("min", {
                "title": _("Min"),
                "sortable": False}),
            ("max", {
                "title": _("Max"),
                "sortable": False}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys()
            }
        ]

    def update(self):
        """Update hook
        """
        super(ReferenceResultsView, self).update()
        self.categories.sort()

    @view.memoize
    def show_categories_enabled(self):
        """Check in the setup if categories are enabled
        """
        return self.context.bika_setup.getCategoriseAnalysisServices()

    @view.memoize
    def get_reference_results(self):
        """Return a mapping of Analysis Service -> Reference Results
        """
        referenceresults = self.context.getReferenceResults()
        return dict(map(lambda rr: (rr.get("uid"), rr), referenceresults))

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """

        obj = api.get_object(obj)
        uid = api.get_uid(obj)
        url = api.get_url(obj)
        title = api.get_title(obj)

        # get the category
        if self.show_categories_enabled():
            category = obj.getCategoryTitle()
            if category not in self.categories:
                self.categories.append(category)
            item["category"] = category

        ref_results = self.get_reference_results()
        ref_result = ref_results.get(uid)

        item["Title"] = title
        item["replace"]["Title"] = get_link(url, value=title)
        item["result"] = ref_result.get("result")
        item["min"] = ref_result.get("min")
        item["max"] = ref_result.get("max")
        item["error"] = ref_result.get("error")

        # Icons
        after_icons = ""
        if obj.getAccredited():
            after_icons += get_image(
                "accredited.png", title=_("Accredited"))
        if obj.getAttachmentOption() == "r":
            after_icons += get_image(
                "attach_reqd.png", title=_("Attachment required"))
        if obj.getAttachmentOption() == "n":
            after_icons += get_image(
                "attach_no.png", title=_("Attachment not permitted"))
        if after_icons:
            item["after"]["Title"] = after_icons

        return item


class ReferenceSamplesView(BikaListingView):
    """Main reference samples folder view
    """

    def __init__(self, context, request):
        super(ReferenceSamplesView, self).__init__(context, request)

        self.catalog = "bika_catalog"

        self.contentFilter = {
            "portal_type": "ReferenceSample",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {"query": ["/"], "level": 0},
        }

        self.context_actions = {}
        self.title = self.context.translate(_("Reference Samples"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/referencesample_big.png")

        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("ID", {
                "title": _("ID"),
                "index": "id"}),
            ("Title", {
                "title": _("Title"),
                "index": "sortable_title",
                "toggle": True}),
            ("Supplier", {
                "title": _("Supplier"),
                "toggle": True,
                "attr": "aq_parent.Title",
                "replace_url": "aq_parent.absolute_url"}),
            ("Manufacturer", {
                "title": _("Manufacturer"),
                "toggle": True,
                "attr": "getManufacturer.Title",
                "replace_url": "getManufacturer.absolute_url"}),
            ("Definition", {
                "title": _("Reference Definition"),
                "toggle": True,
                "attr": "getReferenceDefinition.Title",
                "replace_url": "getReferenceDefinition.absolute_url"}),
            ("DateSampled", {
                "title": _("Date Sampled"),
                "index": "getDateSampled",
                "toggle": True}),
            ("DateReceived", {
                "title": _("Date Received"),
                "index": "getDateReceived",
                "toggle": True}),
            ("DateOpened", {
                "title": _("Date Opened"),
                "toggle": True}),
            ("ExpiryDate", {
                "title": _("Expiry Date"),
                "index": "getExpiryDate",
                "toggle": True}),
            ("state_title", {
                "title": _("State"),
                "toggle": True}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Current"),
                "contentFilter": {"review_state": "current"},
                "columns": self.columns.keys(),
            }, {
                "id": "expired",
                "title": _("Expired"),
                "contentFilter": {"review_state": "expired"},
                "columns": self.columns.keys(),
            }, {
                "id": "disposed",
                "title": _("Disposed"),
                "contentFilter": {"review_state": "disposed"},
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
        super(ReferenceSamplesView, self).before_render()
        # Don't allow any context actions on the Methods folder
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

        obj = api.get_object(obj)

        # XXX Refactor expiration to a proper place
        # ---------------------------- 8< -------------------------------------
        if item.get("review_state", "current") == "current":
            # Check expiry date
            exdate = obj.getExpiryDate()
            if exdate:
                expirydate = DT2dt(exdate).replace(tzinfo=None)
                if (datetime.today() > expirydate):
                    # Trigger expiration
                    self.workflow.doActionFor(obj, "expire")
                    item["review_state"] = "expired"
                    item["obj"] = obj

        if self.contentFilter.get('review_state', '') \
           and item.get('review_state', '') == 'expired':
            # This item must be omitted from the list
            return None
        # ---------------------------- >8 -------------------------------------

        url = api.get_url(obj)
        id = api.get_id(obj)

        item["ID"] = id
        item["replace"]["ID"] = get_link(url, value=id)
        item["DateSampled"] = self.ulocalized_time(
            obj.getDateSampled(), long_format=True)
        item["DateReceived"] = self.ulocalized_time(obj.getDateReceived())
        item["DateOpened"] = self.ulocalized_time(obj.getDateOpened())
        item["ExpiryDate"] = self.ulocalized_time(obj.getExpiryDate())

        # Icons
        after_icons = ''
        if obj.getBlank():
            after_icons += get_image(
                "blank.png", title=t(_("Blank")))
        if obj.getHazardous():
            after_icons += get_image(
                "hazardous.png", title=t(_("Hazardous")))
        if after_icons:
            item["after"]["ID"] = after_icons

        return item
