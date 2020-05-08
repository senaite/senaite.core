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

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.content.analysisspec import ResultsRangeDict
from bika.lims.interfaces import ISubmitted
from bika.lims.utils import dicts_to_dict
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from bika.lims.utils import logged_in_client
from bika.lims.utils import t
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
            "is_active": True
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
        if self.show_ar_specs():
            columns.append("warn_min")
            columns.append("min")
            columns.append("warn_max")
            columns.append("max")

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {"is_active": True},
                "columns": columns,
                "transitions": [{"id": "disallow-all-possible-transitions"}],
                "custom_transitions": [
                    {
                        "id": "save_analyses",
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
    def show_ar_specs(self):
        """Checks if AR specs should be shown or not
        """
        setup = api.get_setup()
        return setup.getEnableARSpecs()

    @view.memoize
    def get_results_range(self):
        """Get the results Range from the Sample, but gives priority to the
        result ranges set in analyses. This guarantees that result ranges for
        already present analyses are not overriden after form submission
        """
        # Extract the result ranges from Sample analyses
        analyses = self.analyses.values()
        analyses_rrs = map(lambda an: an.getResultsRange(), analyses)
        analyses_rrs = filter(None, analyses_rrs)
        rrs = dicts_to_dict(analyses_rrs, "keyword")

        # Bail out ranges from Sample that are already present in analyses
        sample_rrs = self.context.getResultsRange()
        sample_rrs = filter(lambda rr: rr["keyword"] not in rrs, sample_rrs)
        sample_rrs = dicts_to_dict(sample_rrs, "keyword")

        # Extend result ranges with those from Sample
        rrs.update(sample_rrs)
        return rrs

    @view.memoize
    def get_currency_symbol(self):
        """Get the currency Symbol
        """
        locale = locales.getLocale('en')
        setup = api.get_setup()
        currency = setup.getCurrency()
        return locale.numbers.currencies[currency].symbol

    @view.memoize
    def get_logged_in_client(self):
        """Return the logged in client
        """
        return logged_in_client(self.context)

    def get_editable_columns(self, obj):
        """Return editable fields
        """
        columns = ["min", "max", "warn_min", "warn_max", "Hidden"]
        if not self.get_logged_in_client():
            columns.append("Price")
        return columns

    def folderitems(self):
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

        price = obj.getPrice()
        keyword = obj.getKeyword()

        if uid in self.analyses:
            analysis = self.analyses[uid]
            # Might differ from the service keyword
            keyword = analysis.getKeyword()
            # Mark the row as disabled if the analysis has been submitted
            item["disabled"] = ISubmitted.providedBy(analysis)
            # get the hidden status of the analysis
            hidden = analysis.getHidden()
            # get the price of the analysis
            price = analysis.getPrice()

        # get the specification of this object
        rr = self.get_results_range()
        spec = rr.get(keyword, ResultsRangeDict())

        item["Title"] = obj.Title()
        item["Unit"] = obj.getUnit()
        item["Price"] = price
        item["before"]["Price"] = self.get_currency_symbol()
        item["allow_edit"] = self.get_editable_columns(obj)
        item["selected"] = uid in self.selected
        item["min"] = str(spec.get("min", ""))
        item["max"] = str(spec.get("max", ""))
        item["warn_min"] = str(spec.get("warn_min", ""))
        item["warn_max"] = str(spec.get("warn_max", ""))
        item["Hidden"] = hidden

        # Append info link before the service
        # see: bika.lims.site.coffee for the attached event handler
        item["before"]["Title"] = get_link(
            "analysisservice_info?service_uid={}".format(uid),
            value="<span class='glyphicon glyphicon-info-sign'></span>",
            css_class="service_info")

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
