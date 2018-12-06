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
from bika.lims.content.analysisspec import ResultsRangeDict
from bika.lims.utils import dicts_to_dict
from bika.lims.utils import get_image
from bika.lims.utils import logged_in_client
from bika.lims.utils import t
from bika.lims.workflow import wasTransitionPerformed
from plone.memoize import view
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n.locales import locales


class AnalysisRequestAnalysesView(BikaListingView):
    """AR Manage Analyses View
    """
    template = ViewPageTemplateFile("templates/analysisrequest_analyses.pt")

    def __init__(self, context, request):
        super(AnalysisRequestAnalysesView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "AnalysisService",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "inactive_state": "active"
        }
        self.context_actions = {}
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/analysisservice_big.png"
        )
        self.show_column_toggles = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 999999
        self.show_search = True
        self.fetch_transitions_on_select = False

        self.categories = []
        self.selected = []
        self.do_cats = self.context.bika_setup.getCategoriseAnalysisServices()
        if self.do_cats:
            self.show_categories = True
            self.expand_all_categories = False

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Service"),
                "index": "sortable_title",
                "sortable": False}),
            ("Unit", {
                "title": _("Unit"),
                "sortable": False}),
            ("Hidden", {
                "title": _("Hidden"),
                "sortable": False,
                "type": "boolean"}),
            ("Price", {
                "title": _("Price"),
                "sortable": False}),
            ("Partition", {
                "title": _("Partition"),
                "sortable": False,
                "type": "choices"}),
            ("warn_min", {
                "title": _("Min warn")}),
            ("min", {
                "title": _("Min")}),
            ("warn_max", {
                "title": _("Max warn")}),
            ("max", {
                "title": _("Max")}),
        ))

        columns = ["Title", "Unit", "Hidden", ]
        if self.show_prices():
            columns.append("Price")
        if self.show_partitions():
            columns.append("Partition")
        if self.show_ar_specs():
            columns.append("warn_min")
            columns.append("min")
            columns.append("warn_max")
            columns.append("max")

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {"inactive_state": "active"},
                "columns": columns,
                "transitions": [{"id": "disallow-all-possible-transitions"}],
                "custom_transitions": [
                    {
                        "id": "save_analyses_button",
                        "title": _("Save")
                    }
                ],
            },
        ]

    def update(self):
        """Update hook
        """
        super(AnalysisRequestAnalysesView, self).update()
        analyses = self.context.getAnalyses(full_objects=True)
        self.analyses = dict([(a.getServiceUID(), a) for a in analyses])
        self.selected = self.analyses.keys()

    @view.memoize
    def show_prices(self):
        """Checks if prices should be shown or not
        """
        setup = api.get_setup()
        return setup.getShowPrices()

    @view.memoize
    def show_partitions(self):
        """Checks if partitions should be shown
        """
        setup = api.get_setup()
        return setup.getShowPartitions()

    @view.memoize
    def show_ar_specs(self):
        """Checks if AR specs should be shown or not
        """
        setup = api.get_setup()
        return setup.getEnableARSpecs()

    @view.memoize
    def allow_department_filtering(self):
        """Checks if department filtering is allowed
        """
        setup = api.get_setup()
        return setup.getAllowDepartmentFiltering()

    @view.memoize
    def get_results_range(self):
        """Get the results Range from the AR
        """
        spec = self.context.getResultsRange()
        if spec:
            return dicts_to_dict(spec, "keyword")
        return ResultsRangeDict()

    @view.memoize
    def get_partitions(self):
        """Get the partitions
        """
        sample = self.context.getSample()
        return sample.objectValues("SamplePartition")

    def get_partition(self, analysis):
        """Get the partition of the Analysis
        """
        partition = analysis.getSamplePartition()
        if not partition:
            return self.get_partitions()[0]
        return partition

    @view.memoize
    def get_currency_symbol(self):
        """Get the currency Symbol
        """
        locale = locales.getLocale('en')
        setup = api.get_setup()
        currency = setup.getCurrency()
        return locale.numbers.currencies[currency].symbol

    def is_submitted(self, obj):
        """Check if the "submit" transition was performed
        """
        return wasTransitionPerformed(obj, "submit")

    @view.memoize
    def get_logged_in_client(self):
        """Return the logged in client
        """
        return logged_in_client(self.context)

    def get_editable_columns(self, obj):
        """Return editable fields
        """
        columns = ["Partition", "min", "max", "warn_min", "warn_max", "Hidden"]
        if not self.get_logged_in_client():
            columns.append("Price")
        return columns

    def isItemAllowed(self, obj):
        """Checks if the item can be added to the list depending on the
        department filter. If the analysis service is not assigned to a
        department, show it.
        If department filtering is disabled in bika_setup, will return True.
        """
        if not self.allow_department_filtering():
            return True

        # Gettin the department from analysis service
        obj_dep = obj.getDepartment()
        result = True
        if obj_dep:
            # Getting the cookie value
            cookie_dep_uid = self.request.get(
                "filter_by_department_info", "no")
            # Comparing departments' UIDs
            result = True if obj_dep.UID() in\
                cookie_dep_uid.split(",") else False
            return result
        return result

    def folderitems(self):
        """XXX refactor if possible to non-classic mode
        """
        items = super(AnalysisRequestAnalysesView, self).folderitems()
        self.categories.sort()
        return items

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        # ensure we have an object and not a brain
        obj = api.get_object(obj)
        uid = api.get_uid(obj)

        # settings for this analysis
        service_settings = self.context.getAnalysisServiceSettings(uid)
        hidden = service_settings.get("hidden", obj.getHidden())

        # get the category
        category = obj.getCategoryTitle()
        item["category"] = category
        if category not in self.categories:
            self.categories.append(category)

        parts = filter(api.is_active, self.get_partitions())
        partitions = map(lambda part: {
            "ResultValue": part.Title(), "ResultText": part.getId()}, parts)

        keyword = obj.getKeyword()
        partition = None
        if uid in self.analyses:
            analysis = self.analyses[uid]
            # Might differ from the service keyword
            keyword = analysis.getKeyword()
            # Mark the row as disabled if the analysis is not in an open state
            item["disabled"] = not analysis.isOpen()
            # get the hidden status of the analysis
            hidden = analysis.getHidden()
            # get the partition of the analysis
            partition = self.get_partition(analysis)
        else:
            partition = self.get_partitions()[0]

        # get the specification of this object
        rr = self.get_results_range()
        spec = rr.get(keyword, ResultsRangeDict())

        item["Title"] = obj.Title()
        item["Unit"] = obj.getUnit()
        item["Price"] = obj.getPrice()
        item["before"]["Price"] = self.get_currency_symbol()
        item["allow_edit"] = self.get_editable_columns(obj)
        item["selected"] = uid in self.selected
        item["min"] = str(spec.get("min", ""))
        item["max"] = str(spec.get("max", ""))
        item["warn_min"] = str(spec.get("warn_min", ""))
        item["warn_max"] = str(spec.get("warn_max", ""))
        item["Hidden"] = hidden
        item["Partition"] = partition.getId()
        item["choices"]["Partition"] = partitions

        # Icons
        after_icons = ""
        if obj.getAccredited():
            after_icons += get_image(
                "accredited.png", title=t(_("Accredited")))
        if obj.getAttachmentOption() == "r":
            after_icons += get_image(
                "attach_reqd.png", title=t(_("Attachment required")))
        if obj.getAttachmentOption() == "n":
            after_icons += get_image(
                "attach_no.png", title=t(_('Attachment not permitted')))
        if after_icons:
            item["after"]["Title"] = after_icons

        return item
