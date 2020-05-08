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
from bika.lims import logger
from bika.lims.api.security import check_permission
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import MAX_OPERATORS
from bika.lims.config import MIN_OPERATORS
from bika.lims.permissions import FieldEditSpecification
from bika.lims.utils import dicts_to_dict
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from bika.lims.utils import to_choices
from plone.memoize import view
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget


class AnalysisSpecificationView(BikaListingView):
    """Listing table to display Analysis Specifications
    """

    def __init__(self, context, request):
        super(AnalysisSpecificationView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "AnalysisService",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        self.context_actions = {}

        self.show_column_toggles = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 999999
        self.allow_edit = True
        self.show_search = True
        self.omit_form = True
        self.fetch_transitions_on_select = False

        # Categories
        if self.show_categories_enabled():
            self.categories = []
            self.show_categories = True
            self.expand_all_categories = False

        # Operator Choices
        self.min_operator_choices = to_choices(MIN_OPERATORS)
        self.max_operator_choices = to_choices(MAX_OPERATORS)

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
                "sortable": False}),
            ("warn_min", {
                "title": _("Min warn"),
                "sortable": False}),
            ("min_operator", {
                "title": _("Min operator"),
                "type": "choices",
                "sortable": False}),
            ("min", {
                "title": _("Min"),
                "sortable": False}),
            ("max_operator", {
                "title": _("Max operator"),
                "type": "choices",
                "sortable": False}),
            ("max", {
                "title": _("Max"),
                "sortable": False}),
            ("warn_max", {
                "title": _("Max warn"),
                "sortable": False}),
            ("hidemin", {
                "title": _("< Min"),
                "sortable": False}),
            ("hidemax", {
                "title": _("> Max"),
                "sortable": False}),
            ("rangecomment", {
                "title": _("Range comment"),
                "sortable": False,
                "type": "remarks",
                "toggle": False}),
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
        super(AnalysisSpecificationView, self).update()
        self.allow_edit = self.is_edit_allowed()
        results_range = self.context.getResultsRange()
        self.specification = dicts_to_dict(results_range, "keyword")
        self.dynamic_spec = self.context.getDynamicAnalysisSpec()

    @view.memoize
    def is_edit_allowed(self):
        """Check if edit is allowed
        """
        return check_permission(FieldEditSpecification, self.context)

    @view.memoize
    def show_categories_enabled(self):
        """Check in the setup if categories are enabled
        """
        return self.context.bika_setup.getCategoriseAnalysisServices()

    def get_editable_columns(self):
        """Return editable fields
        """
        columns = ["min", "max", "warn_min", "warn_max", "hidemin", "hidemax",
                   "rangecomment", "min_operator", "max_operator"]
        return columns

    def get_required_columns(self):
        """Return required editable fields
        """
        columns = []
        return columns

    @view.memoize
    def get_dynamic_analysisspecs(self):
        if not self.dynamic_spec:
            return {}
        return self.dynamic_spec.get_by_keyword()

    def folderitems(self):
        items = super(AnalysisSpecificationView, self).folderitems()
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
        url = api.get_url(obj)
        title = api.get_title(obj)
        keyword = obj.getKeyword()

        # dynamic analysisspecs
        dspecs = self.get_dynamic_analysisspecs()
        dspec = dspecs.get(keyword)
        # show the dynamic specification icon next to the Keyword
        if dspec:
            item["before"]["Keyword"] = get_image(
                "dynamic_analysisspec.png",
                title=_("Found Dynamic Analysis Specification for '{}' in '{}'"
                        .format(keyword, self.dynamic_spec.Title())))

        # get the category
        if self.show_categories_enabled():
            category = obj.getCategoryTitle()
            if category not in self.categories:
                self.categories.append(category)
            item["category"] = category

        item["Title"] = title
        item["replace"]["Title"] = get_link(url, value=title)
        item["choices"]["min_operator"] = self.min_operator_choices
        item["choices"]["max_operator"] = self.max_operator_choices
        item["allow_edit"] = self.get_editable_columns()
        item["required"] = self.get_required_columns()

        spec = self.specification.get(keyword, {})

        item["selected"] = spec and True or False
        item["min_operator"] = spec.get("min_operator", "geq")
        item["min"] = spec.get("min", "")
        item["max_operator"] = spec.get("max_operator", "leq")
        item["max"] = spec.get("max", "")
        item["warn_min"] = spec.get("warn_min", "")
        item["warn_max"] = spec.get("warn_max", "")
        item["hidemin"] = spec.get("hidemin", "")
        item["hidemax"] = spec.get("hidemax", "")
        item["rangecomment"] = spec.get("rangecomment", "")

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


class AnalysisSpecificationWidget(TypesWidget):
    """Analysis Specification Widget
    """
    _properties = TypesWidget._properties.copy()
    _properties.update({
        "macro": "bika_widgets/analysisspecificationwidget",
    })

    security = ClassSecurityInfo()

    security.declarePublic("process_form")

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """Return a list of dictionaries fit for AnalysisSpecsResultsField
           consumption.

        If neither hidemin nor hidemax are specified, only services which have
        float()able entries in result,min and max field will be included. If
        hidemin and/or hidemax specified, results might contain empty min
        and/or max fields.
        """
        values = []

        # selected services
        service_uids = form.get("uids", [])

        # return immediately if now services were selected
        if not service_uids:
            return values, {}

        # dynamic analysis specification
        dynamic_spec = {}
        if instance.getDynamicAnalysisSpec():
            dynamic_spec = instance.getDynamicAnalysisSpec().get_by_keyword()

        for uid in service_uids:
            s_min = self._get_spec_value(form, uid, "min")
            s_max = self._get_spec_value(form, uid, "max")

            if not s_min and not s_max:
                service = api.get_object_by_uid(uid)
                keyword = service.getKeyword()
                if not dynamic_spec.get(keyword):
                    # If user has not set value neither for min nor max, omit
                    # this record. Otherwise, since 'min' and 'max' are defined
                    # as mandatory subfields, the following message will appear
                    # after submission: "Specifications is required, please
                    # correct."
                    continue
                s_min = 0
                s_max = 0

            # TODO: disallow this case in the UI
            if s_min and s_max:
                if float(s_min) > float(s_max):
                    logger.warn("Min({}) > Max({}) is not allowed"
                                .format(s_min, s_max))
                    continue

            min_operator = self._get_spec_value(
                form, uid, "min_operator", check_floatable=False)
            max_operator = self._get_spec_value(
                form, uid, "max_operator", check_floatable=False)

            service = api.get_object_by_uid(uid)
            subfield_values = {
                "keyword": service.getKeyword(),
                "uid": uid,
                "min_operator": min_operator,
                "min": s_min,
                "max_operator": max_operator,
                "max": s_max,
                "warn_min": self._get_spec_value(form, uid, "warn_min"),
                "warn_max": self._get_spec_value(form, uid, "warn_max"),
                "hidemin": self._get_spec_value(form, uid, "hidemin"),
                "hidemax": self._get_spec_value(form, uid, "hidemax"),
                "rangecomment": self._get_spec_value(form, uid, "rangecomment",
                                                     check_floatable=False)
            }

            # Include values from other subfields that might be added
            # by other add-ons independently via SchemaModifier
            for subfield in field.subfields:
                if subfield not in subfield_values.keys():
                    subfield_values.update({
                        subfield: self._get_spec_value(form, uid, subfield)
                    })

            values.append(subfield_values)

        return values, {}

    def _get_spec_value(self, form, uid, key, check_floatable=True,
                        default=''):
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
        if not check_floatable:
            return value
        return api.is_floatable(value) and value or default

    security.declarePublic("AnalysisSpecificationResults")

    def AnalysisSpecificationResults(self, field, allow_edit=False):
        """Render Analyses Specifications Table
        """
        instance = getattr(self, "instance", field.aq_parent)
        table = api.get_view("table_analysis_specifications",
                             context=instance,
                             request=self.REQUEST)
        # Call listing hooks
        table.update()
        table.before_render()
        return table.ajax_contents_table()


registerWidget(AnalysisSpecificationWidget,
               title="Analysis Specification Results",
               description=("Analysis Specification Results"))
