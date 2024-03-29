# -*- coding: utf-8 -*-

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
        bika_setup = api.get_bika_setup()
        return bika_setup.getCategoriseAnalysisServices()

    @view.memoize
    def show_prices(self):
        """Checks if prices should be shown or not
        """
        bika_setup = api.get_setup()
        return bika_setup.getShowPrices()

    @view.memoize
    def get_currency_symbol(self):
        """Get the currency Symbol
        """
        locale = locales.getLocale("en")
        bika_setup = api.get_bika_setup()
        currency = bika_setup.getCurrency()
        return locale.numbers.currencies[currency].symbol

    @view.memoize
    def get_decimal_mark(self):
        """Returns the decimal mark
        """
        bika_setup = api.get_bika_setup()
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

    @view.memoize
    def get_editable_columns(self):
        """Return editable fields
        """
        columns = []
        if self.is_edit_allowed():
            columns = ["Hidden"]
        return columns

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
        for uid in selected:
            records.append({
                "uid": uid,
                "hidden": hidden_services.get(uid) == "on",
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

        hidden = False
        # get the hidden setting from the records
        if self.records.get(uid):
            record = self.records.get(uid, {}) or {}
            hidden = record.get("hidden", False)
        else:
            # get the default value from the service
            hidden = obj.getHidden()

        item["replace"]["Title"] = get_link(url, value=title)
        item["Price"] = self.format_price(obj.Price)
        item["allow_edit"] = self.get_editable_columns()
        item["selected"] = False
        item["Hidden"] = hidden
        item["replace"]["Hidden"] = _("Yes") if hidden else _("No")
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

        # Unit
        unit = obj.getUnit()
        item["Unit"] = unit or ""
        item["replace"]["Unit"] = unit and format_supsub(unit) or ""

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
