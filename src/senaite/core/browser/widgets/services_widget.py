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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.api.security import check_permission
from bika.lims.utils import format_supsub
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from plone.memoize import view
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.permissions import FieldEditProfiles
from senaite.core.z3cform.widgets.listing.view import DefaultListingWidget
from zope.i18n.locales import locales


class ServicesWidget(DefaultListingWidget):
    """Listing widget for Analysis Services
    """
    def __init__(self, field, request):
        super(ServicesWidget, self).__init__(field, request)

        self.catalog = SETUP_CATALOG
        self.contentFilter = {
            "portal_type": "AnalysisService",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "is_active": True,
        }

        # group the current records by UID
        self.records = {}
        for record in self.get_value():
            uid = record.get("uid")
            self.records[uid] = record

        # listing config
        self.allow_edit = True
        self.context_actions = {}
        self.fetch_transitions_on_select = False
        self.omit_form = True
        self.pagesize = 999999
        self.show_column_toggles = False
        self.show_search = True
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.show_table_footer = False

        # Categories
        if self.show_categories_enabled():
            self.categories = []
            self.show_categories = True
            self.expand_all_categories = False

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _(
                    u"listing_services_column_title",
                    default=u"Service"
                ),
                "index": "sortable_title",
                "sortable": False
            }),
            ("Keyword", {
                "title": _(
                    u"listing_services_column_keyword",
                    default=u"Keyword"
                ),
                "sortable": False
            }),
            ("Methods", {
                "title": _(
                    u"listing_services_column_methods",
                    default=u"Methods"
                ),
                "sortable": False
            }),
            ("Unit", {
                "title": _(
                    u"listing_services_column_unit",
                    default=u"Unit"
                ),
                "sortable": False
            }),
            ("Price", {
                "title": _(
                    u"listing_services_column_price",
                    default=u"Price"
                ),
                "sortable": False,
            }),
            ("Hidden", {
                "title": _(
                    u"listing_services_column_hidden",
                    default=u"Hidden"
                ),
                "sortable": False,
            }),
        ))

        cols = self.columns.keys()
        if not self.show_prices():
            cols.remove("Price")

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_services_state_all",
                    default=u"All"
                ),
                "contentFilter": {},
                "transitions": [{"id": "disallow-all-possible-transitions"}],
                "columns": cols,
            },
        ]

    @view.memoize
    def show_categories_enabled(self):
        """Check in the setup if categories are enabled
        """
        bika_setup = api.get_senaite_setup()
        return bika_setup.getCategoriseAnalysisServices()

    @view.memoize
    def show_prices(self):
        """Checks if prices should be shown or not
        """
        bika_setup = api.get_senaite_setup()
        return bika_setup.getShowPrices()

    @view.memoize
    def get_currency_symbol(self):
        """Get the currency Symbol
        """
        locale = locales.getLocale("en")
        bika_setup = api.get_senaite_setup()
        currency = bika_setup.getCurrency()
        return locale.numbers.currencies[currency].symbol

    @view.memoize
    def get_decimal_mark(self):
        """Returns the decimal mark
        """
        bika_setup = api.get_senaite_setup()
        return bika_setup.getDecimalMark()

    @view.memoize
    def format_price(self, price):
        """Formats the price with the set decimal mark and correct currency
        """
        return u"{} {}{}{:02d}".format(
            self.get_currency_symbol(),
            price[0],
            self.get_decimal_mark(),
            price[1],
        )

    @view.memoize
    def is_edit_allowed(self):
        """Check if edit is allowed
        """
        return check_permission(FieldEditProfiles, self.context)

    def get_editable_columns(self):
        """Return editable fields
        """
        columns = []
        if self.is_edit_allowed():
            columns = ["Hidden"]
        return columns

    def get_record_value(self, uid, key, default):
        """Get a value from the saved records or return default

        :param uid: UID of the service
        :param key: key to look up in the record
        :param default: fallback value if not found
        """
        record = self.records.get(uid) or {}
        return record.get(key, default)

    def get_unit_vocabulary(self, service):
        """Returns a vocabulary with all the units available

        The vocabulary is a list of dictionaries. Each dictionary
        has the following structure:

            {"ResultValue": <unit>,
             "ResultText": <unit>}

        :param service: A single service object
        :returns: A list of dicts
        """
        # Strip surrounding whitespace from configured unit choices so
        # typos like "mg/L " don't break the round-trip with the
        # service/analysis stored Unit value.
        return [
            {"ResultValue": value, "ResultText": value}
            for value in (u["value"].strip() for u in service.getUnitChoices())
        ]

    def extract(self):
        """Extract the value from the request for the field
        """
        form = self.request.form
        selected = form.get(self.select_checkbox_name, [])

        if not selected:
            return []

        # extract the data from the form for the field
        records = []
        hidden_services = form.get("Hidden", {})
        # Unit comes as a list of dicts from the listing form
        units = form.get("Unit", [])
        if isinstance(units, list):
            custom_units = units[0] if units else {}
        elif isinstance(units, dict):
            custom_units = units
        else:
            custom_units = {}

        for uid in selected:
            records.append({
                "uid": uid,
                "hidden": hidden_services.get(uid) == "on",
                "unit": custom_units.get(uid),
            })

        return records

    def folderitems(self):
        items = super(ServicesWidget, self).folderitems()
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
        item = super(ServicesWidget, self).folderitem(obj, item, index)

        # ensure we have an object and not a brain
        obj = api.get_object(obj)
        uid = api.get_uid(obj)
        url = api.get_url(obj)
        title = api.get_title(obj)
        keyword = obj.getKeyword()

        # get the category
        if self.show_categories_enabled():
            category = obj.getCategoryTitle()
            if category not in self.categories:
                self.categories.append(category)
            item["category"] = category

        item["replace"]["Title"] = get_link(url, value=title)
        item["Price"] = self.format_price(obj.Price)
        item["allow_edit"] = self.get_editable_columns()
        item["selected"] = False
        item["selected"] = uid in self.records
        item["Keyword"] = keyword
        item["replace"]["Keyword"] = "<code>{}</code>".format(keyword)

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

        # Apply hidden settings
        hidden = self.get_record_value(uid, "hidden", obj.getHidden())
        item["Hidden"] = hidden
        item["replace"]["Hidden"] = _("Yes") if hidden else _("No")

        # Apply unit settings. Strip surrounding whitespace so the
        # stored Unit matches the (also-stripped) values in the unit
        # choices dropdown built by `get_unit_vocabulary`.
        unit = self.get_record_value(uid, "unit", obj.getUnit())
        unit = (unit or "").strip()
        item["Unit"] = unit
        item["replace"]["Unit"] = format_supsub(unit) if unit else ""
        unit_choices = self.get_unit_vocabulary(obj)
        if unit_choices:
            item["choices"]["Unit"] = unit_choices
            item["allow_edit"].append("Unit")

        # Icons
        after_icons = ""
        if obj.getAccredited():
            after_icons += get_image(
                "accredited.png", title=_("Accredited"))
        if obj.getAttachmentRequired():
            after_icons += get_image(
                "attach_reqd.png", title=_("Attachment required"))
        if after_icons:
            item["after"]["Title"] = after_icons

        return item
