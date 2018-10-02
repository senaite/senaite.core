# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from zope.i18n.locales import locales

ALLOW_EDIT = ["LabManager", "Manager"]


# TODO: Separate widget and view into own modules!


class AnalysisProfileAnalysesView(BikaListingView):
    """View to display Analyses table for an Analysis Profile.
    """

    def __init__(self, context, request, fieldvalue=[], allow_edit=False):
        super(AnalysisProfileAnalysesView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "AnalysisService",
            "inactive_state": "active",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_column_toggles = False
        self.show_select_column = True
        self.allow_edit = allow_edit
        self.form_id = "analyses"
        self.profile = None
        self.pagesize = 999999
        self.categories = []
        self.do_cats = self.context.bika_setup.getCategoriseAnalysisServices()
        self.currency_symbol = self.get_currency_symbol()
        self.decimal_mark = self.get_decimal_mark()
        if self.do_cats:
            self.pagesize = 999999  # hide batching controls
            self.show_categories = True
            self.expand_all_categories = False
            self.ajax_categories = True
            self.ajax_categories_url = self.context.absolute_url() + \
                "/analysisprofile_analysesview"
            self.category_index = "getCategoryTitle"

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Service"),
                "index": "sortable_title",
                "sortable": False}),
            ("Keyword", {
                "title": _("Keyword"),
                "sortable": False}),
            ("Methods", {
                "title": _("Methods"),
                "sortable": False}),
            ("Unit", {
                "title": _("Unit"),
                "index": "getUnit",
                "sortable": False,
            }),
            ("Price", {
                "title": _("Price"),
                "sortable": False,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {"inactive_state": "active"},
                "transitions": [],
                "columns": self.columns.keys(),
            },
        ]

        if not self.context.bika_setup.getShowPrices():
            self.review_states[0]["columns"].remove("Price")

        self.fieldvalue = fieldvalue
        self.selected = [x.UID() for x in fieldvalue]

        if self.aq_parent.portal_type == "AnalysisProfile":
            # Custom settings for the Analysis Services assigned to
            # the Analysis Profile
            # https://jira.bikalabs.com/browse/LIMS-1324
            self.profile = self.aq_parent
            self.columns["Hidden"] = {
                "title": _("Hidden"),
                "sortable": False,
                "type": "boolean",
            }
            self.review_states[0]["columns"].append("Hidden")

    def get_currency_symbol(self):
        """Returns the locale currency symbol
        """
        currency = self.context.bika_setup.getCurrency()
        locale = locales.getLocale("en")
        locale_currency = locale.numbers.currencies.get(currency)
        if locale_currency is None:
            return "$"
        return locale_currency.symbol

    def format_price(self, price):
        """Formats the price with the set decimal mark and correct currency
        """
        return u"{} {}{}{:02d}".format(
            self.currency_symbol,
            price[0],
            self.decimal_mark,
            price[1],
        )

    def get_decimal_mark(self):
        """Returns the decimal mark
        """
        return self.context.bika_setup.getDecimalMark()

    def folderitems(self):
        """Processed once for all analyses
        """
        # XXX: Should be done via the Worflow
        # Check edit permissions
        self.allow_edit = False
        member = api.get_current_user()
        roles = member.getRoles()
        if set(roles).intersection(ALLOW_EDIT):
            self.allow_edit = True
        items = super(AnalysisProfileAnalysesView, self).folderitems()
        self.categories.sort()
        return items

    def folderitem(self, obj, item, index):
        """Processed once per analysis
        """
        cat = obj.getCategoryTitle()
        # Category (upper C) is for display column value
        item["Category"] = cat
        if self.do_cats:
            # category is for bika_listing to groups entries
            item["category"] = cat
            if cat not in self.categories:
                self.categories.append(cat)

        analyses = [a.UID() for a in self.fieldvalue]

        item["selected"] = item["uid"] in analyses
        item["class"]["Title"] = "service_title"

        # Price
        item["Price"] = self.format_price(obj.Price)
        item["class"]["Price"] = "nowrap"

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

        if self.profile:
            # Display analyses for this Analysis Service in results?
            ser = self.profile.getAnalysisServiceSettings(obj.UID())
            item["allow_edit"] = ["Hidden", ]
            item["Hidden"] = ser.get("hidden", obj.getHidden())

        # Add methods
        methods = obj.getMethods()
        if methods:
            links = map(
                lambda m: get_link(
                    m.absolute_url(), value=m.Title(), css_class="link"),
                methods)
            item["replace"]["Methods"] = ", ".join(links)
        else:
            item["methods"] = ""

        return item


class AnalysisProfileAnalysesWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/analysisprofileanalyseswidget",
        'helper_js': ("bika_widgets/analysisprofileanalyseswidget.js",),
        'helper_css': ("bika_widgets/analysisprofileanalyseswidget.css",),
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """ Return a list of dictionaries fit for AnalysisProfile/Analyses field
            consumption.
        """
        service_uids = form.get("uids", None)

        # remember the context, because we need to pass that later to the
        # listing view (see method `Analyses` below)
        self.instance = instance

        if instance.portal_type == "AnalysisProfile":
            # Hidden analyses?
            outs = []
            hiddenans = form.get("Hidden", {})
            if service_uids:
                for uid in service_uids:
                    hidden = hiddenans.get(uid, "")
                    hidden = True if hidden == "on" else False
                    outs.append({"uid": uid, "hidden": hidden})
            instance.setAnalysisServicesSettings(outs)

        return service_uids, {}

    security.declarePublic("Analyses")

    def Analyses(self, field, allow_edit=False):
        """Render listing with categorized services.

        :param field: Contains the schema field with a list of services in it
        """
        fieldvalue = getattr(field, field.accessor)()

        # N.B. we do not want to pass the field as the context to
        # AnalysisProfileAnalysesView, but rather the holding instance
        instance = getattr(self, "instance", field.aq_parent)
        view = AnalysisProfileAnalysesView(instance,
                                           self.REQUEST,
                                           fieldvalue=fieldvalue,
                                           allow_edit=allow_edit)
        return view.contents_table(table_only=True)


registerWidget(AnalysisProfileAnalysesWidget,
               title='Analysis Profile Analyses selector',
               description=('Analysis Profile Analyses selector'),)
