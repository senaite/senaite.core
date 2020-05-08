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

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from plone.memoize import view
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget


class ServicesView(BikaListingView):
    """Listing table to display Analyses Services
    """

    def __init__(self, context, request):
        super(ServicesView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "AnalysisService",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        if context.getRestrictToMethod():
            method_uid = context.getMethodUID()
            if method_uid:
                self.contentFilter.update({
                    "method_available_uid": method_uid
                })

        self.context_actions = {}

        # selected services UIDs
        self.selected_services_uids = self.get_assigned_services_uids()

        self.show_column_toggles = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 999999
        self.allow_edit = True
        self.show_search = True
        # omit the outer form
        self.omit_form = True
        # no need to fetch the allowed transitions on select
        self.fetch_transitions_on_select = False

        # Categories
        if self.show_categories_enabled():
            self.categories = []
            self.show_categories = True
            self.expand_all_categories = False

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Service")}),
            ("Keyword", {
                "title": _("Keyword"),
                "index": "getKeyword"}),
            ("Methods", {
                "title": _("Methods")}),
            ("Calculation", {
                "title": _("Calculation")}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {"is_active": True},
                "transitions": [{"id": "disallow-all-possible-transitions"}],
                "columns": self.columns.keys(),
            }
        ]

    def update(self):
        """Update hook
        """
        super(ServicesView, self).update()

    @view.memoize
    def show_categories_enabled(self):
        """Check in the setup if categories are enabled
        """
        return self.context.bika_setup.getCategoriseAnalysisServices()

    @view.memoize
    def get_assigned_services(self):
        """Return the assigned services
        """
        return self.context.getService()

    @view.memoize
    def get_assigned_services_uids(self):
        """Return the UIDs of the assigned services
        """
        return map(api.get_uid, self.get_assigned_services())

    def folderitems(self):
        items = super(ServicesView, self).folderitems()
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
        url = api.get_url(obj)
        title = api.get_title(obj)

        # get the category
        if self.show_categories_enabled():
            category = obj.getCategoryTitle()
            if category not in self.categories:
                self.categories.append(category)
            item["category"] = category

        item["replace"]["Title"] = get_link(url, value=title)
        item["selected"] = False
        item["selected"] = uid in self.selected_services_uids

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

        calculation = obj.getCalculation()
        if calculation:
            title = calculation.Title()
            url = calculation.absolute_url()
            item["Calculation"] = title
            item["replace"]["Calculation"] = get_link(url, value=title)
        else:
            item["Calculation"] = ""

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


class ServicesWidget(TypesWidget):
    """Analyses Services Widget
    """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        "macro": "bika_widgets/serviceswidget",
    })

    security = ClassSecurityInfo()

    security.declarePublic("process_form")

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Return UIDs of the selected services
        """
        service_uids = form.get("uids", [])
        return service_uids, {}

    security.declarePublic("Services")

    def Services(self, field, show_select_column=True):
        """Render Analyses Services Listing Table
        """

        instance = getattr(self, "instance", field.aq_parent)
        table = api.get_view("table_analyses_services",
                             context=instance,
                             request=self.REQUEST)
        # Call listing hooks
        table.update()
        table.before_render()
        return table.ajax_contents_table()


registerWidget(ServicesWidget,
               title="Analysis Services",
               description=("Categorised AnalysisService selector."),)
