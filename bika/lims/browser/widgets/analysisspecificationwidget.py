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
from bika.lims import logger
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import MIN_OPERATORS, MAX_OPERATORS
from bika.lims.utils import get_image, to_choices
from bika.lims.utils import get_link
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget

ALLOW_EDIT = ["LabManager", "Manager"]


# TODO: Separate widget and view into own modules!


class AnalysisSpecificationView(BikaListingView):
    """Renders a listing to display an Analysis Services (AS) table for an
       Analysis Specification.
    """

    def __init__(self, context, request, fieldvalue=[], allow_edit=True):
        BikaListingView.__init__(self, context, request)

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
        self.show_select_column = False
        self.pagesize = 999999
        self.allow_edit = allow_edit
        self.show_categories = True
        self.form_id = "analysisspec"
        # self.expand_all_categories = False
        self.ajax_categories = True
        self.ajax_categories_url = "{}/{}".format(
            self.context.absolute_url(),
            "/analysis_spec_widget_view"
        )
        self.category_index = "getCategoryTitle"

        self.specsresults = {}
        for specresults in fieldvalue:
            self.specsresults[specresults["keyword"]] = specresults

        self.columns = collections.OrderedDict((
            ("service", {
                "title": _("Service"),
                "index": "sortable_title",
                "sortable": False}),
            ("keyword", {
                "title": _("Keyword"),
                "sortable": False}),
            ("methods", {
                "title": _("Methods"),
                "sortable": False}),
            ("unit", {
                "title": _("Unit"),
                "sortable": False}),
            ("service", {
                "title": _("Service"),
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
                "toggle": False}),
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

    def get_sorted_categories(self, items):
        """Extracts the categories from the items
        """

        # XXX should be actually following the sortKey as well
        categories = filter(
            None, set(map(lambda item: item.get("category"), items)))

        return sorted(categories)

    def get_services(self):
        """returns all services
        """
        catalog = api.get_tool("bika_setup_catalog")
        query = self.contentFilter.copy()
        # The contentFilter query get changed by the listing view to show only
        # services in a category. This update ensures that the sorting is kept
        # correct and that no inactive services are displayed.
        query.update({
            "inactive_state": "active",
            "sort_on": self.sort_on,
            "sort_order": self.sort_order,
        })
        logger.info("AnalysisSpecificationWidget::query=%r" % query)
        return catalog(query)

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        service = api.get_object(obj)

        if service.getKeyword() in self.specsresults:
            specresults = self.specsresults[service.getKeyword()]
        else:
            specresults = {
                "keyword": service.getKeyword(),
                "min_operator": "",
                "min": "",
                "max_operator": "",
                "max": "",
                "warn_min": "",
                "warn_max": "",
                "hidemin": "",
                "hidemax": "",
                "rangecomment": "",
            }

        # Icons
        after_icons = ""
        if service.getAccredited():
            after_icons += get_image(
                "accredited.png", title=_("Accredited"))
        if service.getAttachmentOption() == "r":
            after_icons += get_image(
                "attach_reqd.png", title=_("Attachment required"))
        if service.getAttachmentOption() == "n":
            after_icons += get_image(
                "attach_no.png", title=_("Attachment not permitted"))

        state = api.get_workflow_status_of(service, state_var="inactive_state")
        unit = service.getUnit()

        item = {
            "obj": service,
            "id": service.getId(),
            "uid": service.UID(),
            "keyword": service.getKeyword(),
            "title": service.Title(),
            "unit": unit,
            "category": service.getCategoryTitle(),
            "selected": service.getKeyword() in self.specsresults.keys(),
            "type_class": "contenttype-ReferenceResult",
            "url": service.absolute_url(),
            "relative_url": service.absolute_url(),
            "view_url": service.absolute_url(),
            "service": service.Title(),
            "min_operator": specresults.get("min_operator", "geq"),
            "min": specresults.get("min", ""),
            "max_operator": specresults.get("max_operator", "leq"),
            "max": specresults.get("max", ""),
            "warn_min": specresults.get("warn_min", ""),
            "warn_max": specresults.get("warn_max", ""),
            "hidemin": specresults.get("hidemin", ""),
            "hidemax": specresults.get("hidemax", ""),
            "rangecomment": specresults.get("rangecomment", ""),
            "replace": {},
            "before": {},
            "after": {
                "service": after_icons,
            },
            "choices": {
                "min_operator": to_choices(MIN_OPERATORS),
                "max_operator": to_choices(MAX_OPERATORS),
            },
            "class": "state-%s" % (state),
            "state_class": "state-%s" % (state),
            "allow_edit": ["min", "max", "warn_min", "warn_max", "hidemin",
                           "hidemax", "rangecomment", "min_operator",
                           "max_operator"],
            "table_row_class": "even",
            "required": ["min_operator", "max_operator"]
        }

        # Add methods
        methods = service.getMethods()
        if methods:
            links = map(
                lambda m: get_link(
                    m.absolute_url(), value=m.Title(), css_class="link"),
                methods)
            item["replace"]["methods"] = ", ".join(links)
        else:
            item["methods"] = ""

        return item

    def folderitems(self):
        """Custom folderitems

        :returns: listing items
        """

        # XXX: Should be done via the Worflow
        # Check edit permissions
        self.allow_edit = False
        member = api.get_current_user()
        roles = member.getRoles()
        if set(roles).intersection(ALLOW_EDIT):
            self.allow_edit = True

        # Analysis Services retrieval and custom item creation
        items = []

        services = self.get_services()
        for num, service in enumerate(services):
            item = self.folderitem(service, {}, num)
            if item:
                items.append(item)

        self.categories = self.get_sorted_categories(items)

        return items


class AnalysisSpecificationWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/analysisspecificationwidget",
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
        if "service" not in form:
            return values, {}

        for uid, keyword in form["keyword"][0].items():
            s_min = self._get_spec_value(form, uid, "min")
            s_max = self._get_spec_value(form, uid, "max")
            if not s_min and not s_max:
                # If user has not set value neither for min nor max, omit this
                # record. Otherwise, since 'min' and 'max' are defined as
                # mandatory subfields, the following message will appear after
                # submission: "Specifications is required, please correct."
                continue
            min_operator = self._get_spec_value(form, uid, "min_operator",
                                                check_floatable=False)
            max_operator = self._get_spec_value(form, uid, "max_operator",
                                                check_floatable=False)
            if not min_operator and not max_operator:
                # Values for min operator and max operator are required
                continue

            values.append({
                "keyword": keyword,
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
                                                     check_floatable=False)})
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
        """Render listing with categorized services.

        :param field: Contains the schema field with a list of services in it
        """
        fieldvalue = getattr(field, field.accessor)()

        # N.B. we do not want to pass the field as the context to
        # AnalysisProfileAnalysesView, but rather the holding instance
        instance = getattr(self, "instance", field.aq_parent)
        view = AnalysisSpecificationView(instance,
                                         self.REQUEST,
                                         fieldvalue=fieldvalue,
                                         allow_edit=allow_edit)

        return view.contents_table(table_only=True)


registerWidget(AnalysisSpecificationWidget,
               title="Analysis Specification Results",
               description=("Analysis Specification Results"))
