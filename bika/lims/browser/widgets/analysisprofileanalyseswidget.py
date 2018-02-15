# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from zope.i18n.locales import locales


class AnalysisProfileAnalysesView(BikaListingView):
    """View to display Analyses table for an Analysis Profile.
    """

    def __init__(self, context, request, fieldvalue=[], allow_edit=False):
        super(AnalysisProfileAnalysesView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "AnalysisService",
            "sort_on": "sortable_title",
            "inactive_state": "active",
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
        if self.do_cats:
            self.pagesize = 999999  # hide batching controls
            self.show_categories = True
            self.expand_all_categories = False
            self.ajax_categories = True
            self.ajax_categories_url = self.context.absolute_url() + \
                "/analysisprofile_analysesview"
            self.category_index = "getCategoryTitle"

        self.columns = {
            "Title": {
                "title": _("Service"),
                "index": "sortable_title",
                "sortable": False,
            },
            "Unit": {
                "title": _("Unit"),
                "index": "getUnit",
                "sortable": False,
            },
            "Price": {
                "title": _("Price"),
                "sortable": False,
            },
        }

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": [
                    "Title",
                    "Unit",
                    "Price",
                ],
                "transitions": [
                    {"id": "empty"},
                ],
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
            self.review_states[0]["columns"].insert(1, "Hidden")

    def folderitems(self):
        """Processed once for all analyses
        """
        mtool = getToolByName(self.context, "portal_membership")
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        self.allow_edit = "LabManager" in roles or "Manager" in roles
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

        calculation = obj.getCalculation()
        item["Calculation"] = calculation and calculation.Title()

        locale = locales.getLocale("en")
        currency = self.context.bika_setup.getCurrency()
        symbol = locale.numbers.currencies[currency].symbol
        item["Price"] = u"{} {}".format(symbol, obj.getPrice())
        item["class"]["Price"] = "nowrap"

        after_icons = ""
        if obj.getAccredited():
            after_icons += u"<img src='{}/++resource++bika.lims.images/accredited.png' title='{}'>".format(
                self.context.absolute_url(), _("Accredited"))
        if obj.getReportDryMatter():
            after_icons += u"<img src='{}/++resource++bika.lims.images/dry.png' title='{}'>".format(
                self.context.absolute_url(), _("Can be reported as dry matter"))
        if obj.getAttachmentOption() == "r":
            after_icons += u"<img src='{}/++resource++bika.lims.images/attach_reqd.png' title='{}'>".format(
                self.context.absolute_url(), _("Attachment required"))
        if obj.getAttachmentOption() == "n":
            after_icons += u"<img src='%s/++resource++bika.lims.images/attach_no.png' title='%s'>".format(
                self.context.absolute_url(), _('Attachment not permitted'))
        if after_icons:
            item["after"]["Title"] = after_icons

        if self.profile:
            # Display analyses for this Analysis Service in results?
            ser = self.profile.getAnalysisServiceSettings(obj.UID())
            item["allow_edit"] = ["Hidden", ]
            item["Hidden"] = ser.get("hidden", obj.getHidden())

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
        """ Print analyses table
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
