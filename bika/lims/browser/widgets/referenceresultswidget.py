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


class ReferenceResultsView(BikaListingView):
    """Listing table to display Reference Results
    """

    def __init__(self, context, request, fieldvalue=[], allow_edit=True):
        super(ReferenceResultsView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "AnalysisService",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        self.context_actions = {}

        self.show_select_column = True
        self.show_select_all_checkbox = True
        self.pagesize = 999999
        self.allow_edit = True
        self.show_search = False
        self.omit_form = True

        # Categories
        self.categories = []
        if self.show_categories_enabled():
            self.show_categories = True
            self.expand_all_categories = False

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Service"),
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
                "transitions": [{"id": "disallow-all-possible-transitions"}],
                "columns": self.columns.keys(),
            },
        ]

    def update(self):
        """Update hook
        """
        super(ReferenceResultsView, self).update()
        self.categories.sort()
        self.referenceresults = self.get_reference_results()

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

    def get_editable_columns(self):
        """Return editable fields
        """
        columns = ["result", "error", "min", "max"]
        return columns

    def get_required_columns(self):
        """Return required editable fields
        """
        columns = ["result"]
        return columns

    def folderitems(self):
        items = super(ReferenceResultsView, self).folderitems()
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

        rr = self.referenceresults.get(uid, {})
        item["Title"] = title
        item["replace"]["Title"] = get_link(url, value=title)
        item["allow_edit"] = self.get_editable_columns()
        item["required"] = self.get_required_columns()
        item["selected"] = rr and True or False
        item["result"] = rr.get("result", "")
        item["min"] = rr.get("min", "")
        item["max"] = rr.get("max", "")
        item["error"] = rr.get("error", "")

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


class ReferenceResultsWidget(TypesWidget):
    """Reference Results Widget
    """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        "macro": "bika_widgets/referenceresultswidget",
        "helper_js": ("bika_widgets/referenceresultswidget.js",),
        "helper_css": ("bika_widgets/referenceresultswidget.css",)
    })

    security = ClassSecurityInfo()

    security.declarePublic("process_form")

    def process_form(self, instance, field, form,
                     empty_marker=None, emptyReturnsMarker=False):
        """Return a list of dictionaries fit for ReferenceResultsField
        consumption. Only services which have float()able entries in result,min
        and max field will be included. If any of min, max, or result fields
        are blank, the row value is ignored here.
        """
        values = {}

        # Process settings from the reference definition first
        ref_def = form.get("ReferenceDefinition")
        ref_def_uid = ref_def and ref_def[0]
        if ref_def_uid:
            ref_def_obj = api.get_object_by_uid(ref_def_uid)
            ref_results = ref_def_obj.getReferenceResults()
            # store reference results by UID to avoid duplicates
            rr_by_uid = dict(map(lambda r: (r.get("uid"), r), ref_results))
            values.update(rr_by_uid)

        # selected services
        service_uids = form.get("uids", [])

        for uid in service_uids:
            result = self._get_spec_value(form, uid, "result")
            if not result:
                # User has to set a value for result subfield at least
                continue

            # If neither min nor max have been set, assume we only accept a
            # discrete result (like if % of error was 0).
            s_err = self._get_spec_value(form, uid, "error")
            s_min = self._get_spec_value(form, uid, "min", result)
            s_max = self._get_spec_value(form, uid, "max", result)

            # If an error percentage was given, calculate the min/max from the
            # error percentage
            if s_err:
                s_min = float(result) * (1 - float(s_err)/100)
                s_max = float(result) * (1 + float(s_err)/100)

            service = api.get_object_by_uid(uid)
            values[uid] = {
                "keyword": service.getKeyword(),
                "uid": uid,
                "result": result,
                "min": s_min,
                "max": s_max,
                "error": s_err
            }

        return values.values(), {}

    def _get_spec_value(self, form, uid, key, default=''):
        """Returns the value assigned to the passed in key for the analysis
        service uid from the passed in form.

        If check_floatable is true, will return the passed in default if the
        obtained value is not floatable
        :param form: form being submitted
        :param uid: uid of the Analysis Service the specification relates
        :param key: id of the specs param to get (e.g. 'min')
        :param check_floatable: check if the value is floatable
        :param default: fallback value that will be returned by default
        :type default: str, None
        """
        if not form or not uid:
            return default
        values = form.get(key, None)
        if not values or len(values) == 0:
            return default
        value = values[0].get(uid, default)
        return api.is_floatable(value) and value or default

    security.declarePublic("ReferenceResults")

    def ReferenceResults(self, field, allow_edit=False):
        """Render Reference Results Table
        """
        instance = getattr(self, "instance", field.aq_parent)
        table = api.get_view("table_reference_results",
                             context=instance,
                             request=self.REQUEST)
        # Call listing hooks
        table.update()
        table.before_render()
        return table.ajax_contents_table()


registerWidget(ReferenceResultsWidget,
               title="Reference definition results",
               description=("Reference definition results."),)
