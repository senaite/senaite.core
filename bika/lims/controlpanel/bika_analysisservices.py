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
from transaction import savepoint

from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisServices
from bika.lims.permissions import AddAnalysisService
from bika.lims.utils import format_supsub
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from bika.lims.utils import tmpID
from bika.lims.validators import ServiceKeywordValidator
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from zope.i18n.locales import locales
from zope.interface.declarations import implements


class AnalysisServiceCopy(BrowserView):
    template = ViewPageTemplateFile("templates/analysisservice_copy.pt")
    # should never be copied between services
    skip_fieldnames = [
        "UID",
        "id",
        "title",
        "ShortTitle",
        "Keyword",
    ]
    created = []

    def create_service(self, src_uid, dst_title, dst_keyword):
        folder = self.context.bika_setup.bika_analysisservices
        dst_service = _createObjectByType("AnalysisService", folder, tmpID())
        # manually set keyword and title
        dst_service.setKeyword(dst_keyword)
        dst_service.setTitle(dst_title)
        dst_service.unmarkCreationFlag()
        _id = renameAfterCreation(dst_service)
        dst_service = folder[_id]
        return dst_service

    def validate_service(self, dst_service):
        # validate entries
        validator = ServiceKeywordValidator()
        # baseschema uses uniquefieldvalidator on title, this is sufficient.
        res = validator(dst_service.getKeyword(), instance=dst_service)
        if res is not True:
            self.savepoint.rollback()
            self.created = []
            self.context.plone_utils.addPortalMessage(
                safe_unicode(res), "info")
            return False
        return True

    def copy_service(self, src_uid, dst_title, dst_keyword):
        uc = getToolByName(self.context, "uid_catalog")
        src_service = uc(UID=src_uid)[0].getObject()
        dst_service = self.create_service(src_uid, dst_title, dst_keyword)
        if self.validate_service(dst_service):
            # copy field values
            for field in src_service.Schema().fields():
                fieldname = field.getName()
                fieldtype = field.getType()
                if fieldtype == "Products.Archetypes.Field.ComputedField" \
                        or fieldname in self.skip_fieldnames:
                    continue
                value = field.get(src_service)
                if value:
                    # https://github.com/bikalabs/bika.lims/issues/2015
                    if fieldname in ["UpperDetectionLimit",
                                     "LowerDetectionLimit"]:
                        value = str(value)
                    mutator_name = dst_service.getField(fieldname).mutator
                    mutator = getattr(dst_service, mutator_name)
                    mutator(value)
            dst_service.reindexObject()
            return dst_title
        else:
            return False

    def __call__(self):
        uc = getToolByName(self.context, "uid_catalog")
        if "copy_form_submitted" not in self.request:
            uids = self.request.form.get("uids", [])
            self.services = []
            for uid in uids:
                proxies = uc(UID=uid)
                if proxies:
                    self.services.append(proxies[0].getObject())
            return self.template()
        else:
            self.savepoint = savepoint()
            sources = self.request.form.get("uids", [])
            titles = self.request.form.get("dst_title", [])
            keywords = self.request.form.get("dst_keyword", [])
            self.created = []
            for i, s in enumerate(sources):
                if not titles[i]:
                    message = _("Validation failed: title is required")
                    message = safe_unicode(message)
                    self.context.plone_utils.addPortalMessage(message, "info")
                    self.savepoint.rollback()
                    self.created = []
                    break
                if not keywords[i]:
                    message = _("Validation failed: keyword is required")
                    message = safe_unicode(message)
                    self.context.plone_utils.addPortalMessage(message, "info")
                    self.savepoint.rollback()
                    self.created = []
                    break
                title = self.copy_service(s, titles[i], keywords[i])
                if title:
                    self.created.append(title)
            if len(self.created) > 1:
                message = _("${items} were successfully created.",
                            mapping={
                                "items": safe_unicode(
                                    ", ".join(self.created))})
            elif len(self.created) == 1:
                message = _("${item} was successfully created.",
                            mapping={
                                "item": safe_unicode(self.created[0])})
            else:
                message = _("No new items were created.")
            self.context.plone_utils.addPortalMessage(message, "info")
            self.request.response.redirect(self.context.absolute_url())


class AnalysisServicesView(BikaListingView):
    """Listing table view for Analysis Services
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(AnalysisServicesView, self).__init__(context, request)

        self.an_cats = None
        self.an_cats_order = None
        self.catalog = "bika_setup_catalog"

        self.contentFilter = {
            "portal_type": "AnalysisService",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=AnalysisService",
                "permission": AddAnalysisService,
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/analysisservice_big.png"
        )

        self.title = self.context.translate(_("Analysis Services"))
        self.form_id = "list_analysisservices"

        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 25
        self.sort_on = "sortable_title"
        self.categories = []
        self.do_cats = self.context.bika_setup.getCategoriseAnalysisServices()
        self.can_sort = not self.do_cats
        self.currency_symbol = self.get_currency_symbol()
        self.decimal_mark = self.get_decimal_mark()
        if self.do_cats:
            self.pagesize = 999999  # hide batching controls
            self.show_categories = True
            self.expand_all_categories = False

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Service"),
                "index": "sortable_title",
                "replace_url": "getURL",
                "sortable": self.can_sort}),
            ("Keyword", {
                "title": _("Keyword"),
                "index": "getKeyword",
                "attr": "getKeyword",
                "sortable": self.can_sort}),
            ("Category", {
                "title": _("Category"),
                "attr": "getCategoryTitle",
                "sortable": self.can_sort}),
            ("Methods", {
                "title": _("Methods"),
                "sortable": self.can_sort}),
            ("Department", {
                "title": _("Department"),
                "toggle": False,
                "sortable": self.can_sort}),
            ("Unit", {
                "title": _("Unit"),
                "sortable": False}),
            ("Price", {
                "title": _("Price"),
                "sortable": self.can_sort}),
            ("MaxTimeAllowed", {
                "title": _("Max Time"),
                "toggle": False,
                "sortable": self.can_sort}),
            ("DuplicateVariation", {
                "title": _("Dup Var"),
                "toggle": False,
                "sortable": False}),
            ("Calculation", {
                "title": _("Calculation"),
                "sortable": False}),
            ("SortKey", {
                "title": _("Sort Key"),
                "attr": "getSortKey",
                "sortable": False}),
        ))

        copy_transition = {
            "id": "duplicate",
            "title": _("Duplicate"),
            "url": "copy"
        }

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"review_state": "active"},
                "columns": self.columns.keys(),
                "custom_transitions": [copy_transition]
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {"review_state": "inactive"},
                "columns": self.columns.keys(),
                "custom_transitions": [copy_transition]
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
                "custom_transitions": [copy_transition]
            },
        ]

        if not self.context.bika_setup.getShowPrices():
            for i in range(len(self.review_states)):
                self.review_states[i]["columns"].remove("Price")

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)

    def get_decimal_mark(self):
        """Returns the decimal mark
        """
        return self.context.bika_setup.getDecimalMark()

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

    def format_maxtime(self, maxtime):
        """Formats the max time record to a days, hours, minutes string
        """
        minutes = maxtime.get("minutes", "0")
        hours = maxtime.get("hours", "0")
        days = maxtime.get("days", "0")
        # days, hours, minutes
        return u"{}: {} {}: {} {}: {}".format(
            _("days"), days, _("hours"), hours, _("minutes"), minutes)

    def format_duplication_variation(self, variation):
        """Format duplicate variation
        """
        return u"{}{}{:02d}".format(
            variation[0],
            self.decimal_mark,
            variation[1]
        )

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        obj = api.get_object(obj)
        cat = obj.getCategoryTitle()
        cat_order = self.an_cats_order.get(cat)
        if self.do_cats:
            # category groups entries
            item["category"] = cat
            if (cat, cat_order) not in self.categories:
                self.categories.append((cat, cat_order))

        # Category
        category = obj.getCategory()
        if category:
            title = category.Title()
            url = api.get_url(category)
            item["Category"] = title
            item["replace"]["Category"] = get_link(url, value=title)

        # Calculation
        calculation = obj.getCalculation()
        if calculation:
            title = calculation.Title()
            url = api.get_url(calculation)
            item["Calculation"] = title
            item["replace"]["Calculation"] = get_link(url, value=title)

        # Methods
        methods = obj.getMethods()
        if methods:
            links = map(
                lambda m: get_link(
                    m.absolute_url(), value=m.Title(), css_class="link"),
                methods)
            item["replace"]["Methods"] = ", ".join(links)

        # Max time allowed
        maxtime = obj.MaxTimeAllowed
        if maxtime:
            item["MaxTimeAllowed"] = self.format_maxtime(maxtime)

        # Price
        item["Price"] = self.format_price(obj.Price)

        # Duplicate Variation
        dup_variation = obj.DuplicateVariation
        if dup_variation:
            item["DuplicateVariation"] = self.format_duplication_variation(
                dup_variation)

        # Department
        department = obj.getDepartment()
        if department:
            title = api.get_title(department)
            url = api.get_url(department)
            item["replace"]["Department"] = get_link(url, title)

        # Unit
        unit = obj.getUnit()
        item["Unit"] = unit and format_supsub(unit) or ""

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

    def folderitems(self):
        """Sort by Categories
        """
        bsc = getToolByName(self.context, "bika_setup_catalog")
        self.an_cats = bsc(
            portal_type="AnalysisCategory",
            sort_on="sortable_title")
        self.an_cats_order = dict([
            (b.Title, "{:04}".format(a))
            for a, b in enumerate(self.an_cats)])
        items = super(AnalysisServicesView, self).folderitems()
        if self.do_cats:
            self.categories = map(lambda x: x[0],
                                  sorted(self.categories, key=lambda x: x[1]))
        else:
            self.categories.sort()
        return items


schema = ATFolderSchema.copy()
finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)


class AnalysisServices(ATFolder):
    implements(IAnalysisServices)
    displayContentsTab = False
    schema = schema


atapi.registerType(AnalysisServices, PROJECTNAME)
