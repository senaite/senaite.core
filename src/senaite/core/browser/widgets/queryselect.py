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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
import string

from bika.lims import api
from bika.lims import logger
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import StringWidget
from Products.CMFPlone.utils import base_hasattr

# See IReferenceWidgetDataProvider for provided object data
DISPLAY_TEMPLATE = "<div>${Title}</div>"
DEFAULT_SEARCH_CATALOG = "uid_catalog"

# Search index placeholder for dynamic lookup by the search endpoint
SEARCH_INDEX_MARKER = "__search__"


class QuerySelectWidget(StringWidget):
    """Generic select widget to query items from a catalog search
    """
    # CSS class that is picked up by the ReactJS component
    klass = u"senaite-queryselect-widget-input"

    _properties = StringWidget._properties.copy()
    _properties.update({
        "macro": "senaite_widgets/referencewidget",
        "query": {},
        "limit": 5,
        "catalog": None,
        "columns": [],
        "api_url": "referencewidget_search",
        "disabled": False,
        "readonly": False,
        "multi_valued": True,
        "allow_user_value": False,
        "search_wildcard": True,
        "value_key": "title",
        "value_query_index": "title",
        "padding": 3,
        "display_template": None,
        "clear_results_after_select": False,
        "results_table_width": "500px",
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Convert value from textarea field into a list
        """
        value = form.get(field.getName(), "")

        if value and api.is_string(value):
            value = value.split("\r\n")
        elif isinstance(value, list):
            value = value
        else:
            value = []

        # filter out empties
        value = list(filter(None, value))

        return value, {}

    def get_input_widget_attributes(self, context, field, value):
        """Return input widget attributes for the ReactJS component

        This method get called from the page template to populate the
        attributes that are used by the ReactJS widget component.

        :param context: The current context of the field
        :param field: The current field of the widget
        :param value: The curent field value (list of UIDs)
        """
        values = self.get_value(context, field, value)
        template = self.get_display_template(context, field, DISPLAY_TEMPLATE)
        attributes = {
            "data-id": field.getName(),
            "data-name": field.getName(),
            "data-values": values,
            "data-records": dict(zip(values, map(
                lambda ref: self.get_render_data(
                    context, field, ref, template), values))),
            "data-value_key": getattr(self, "value_key", "title"),
            "data-value_query_index": getattr(
                self, "value_query_index", "getId"),
            "data-api_url": getattr(self, "api_url", "referencewidget_search"),
            "data-query": getattr(self, "query", {}),
            "data-catalog": getattr(self, "catalog", DEFAULT_SEARCH_CATALOG),
            "data-search_index": getattr(
                self, "search_index", SEARCH_INDEX_MARKER),
            "data-search_wildcard": getattr(self, "search_wildcard", True),
            "data-allow_user_value": getattr(self, "allow_user_value", False),
            "data-columns": getattr(self, "columns", []),
            "data-display_template": template,
            "data-limit": getattr(self, "limit", 5),
            "data-multi_valued": getattr(self, "multi_valued", True),
            "data-disabled": getattr(self, "disabled", False),
            "data-readonly": getattr(self, "readonly", False),
            "data-clear_results_after_select": getattr(
                self, "clear_results_after_select", False),
        }

        for key, value in attributes.items():
            # Remove the data prefix
            name = key.replace("data-", "", 1)
            # lookup attributes for overrides
            value = self.lookup(name, context, field, default=value)
            # convert all attributes to JSON
            attributes[key] = json.dumps(value)

        return attributes

    def lookup(self, name, context, field, default=None):
        """Check if the context has an override for the given named property

        The context can either define an attribute or a method with the
        following naming convention (all lower case):

            get_wiget_<fieldname>_<propertyname>

        If an attribute or method is found, this value will be returned,
        otherwise the lookup will return the default value

        :param name: The name of a method to lookup
        :param context: The current context of the field
        :param field: The current field of the widget
        :param default: The default property value for the given name
        :returns: New value for the named property
        """

        # check if the current context defines an attribute or a method for the
        # given property following our naming convention
        context_key = "get_widget_{}_{}".format(field.getName(), name).lower()
        if base_hasattr(context, context_key):
            attr = getattr(context, context_key, default)
            if callable(attr):
                # call the context method with additional information
                attr = attr(name=name,
                            widget=self,
                            field=field,
                            context=context,
                            default=default)
            return attr

        # Allow named methods for query/columns
        if name in ["query", "columns"]:
            value = getattr(self, name, None)
            # allow named methods from the context class
            if api.is_string(value):
                method = getattr(context, value, None)
                if callable(method):
                    return method()
            # allow function objects directly
            if callable(value):
                return value()

        # Call custom getter from the widget class
        getter = "get_{}".format(name)
        method = getattr(self, getter, None)
        if callable(method):
            return method(context, field, default=default)

        # return the widget attribute
        return getattr(self, name, default)

    def get_api_url(self, context, field, default=None):
        """JSON API URL to use for this widget

        NOTE: we need to call the search view on the correct context to allow
              context adapter registrations for IReferenceWidgetVocabulary!

        :param context: The current context of the field
        :param field: The current field of the widget
        :param default: The default property value
        :returns: API URL that is contacted when the search changed
        """
        # ensure we have an absolute url for the current context
        url = api.get_url(context)
        # normalize portal factory urls
        url = url.split("/portal_factory")[0]
        # get the API URL
        api_url = getattr(self, "api_url", default)
        # ensure the search path does not contain already the url
        search_path = api_url.split(url)[-1]
        # return the absolute search url
        return "/".join([url, search_path])

    def get_display_template(self, context, field, default=None):
        """Lookup the display template

        :param context: The current context of the field
        :param field: The current field of the widget
        :param default: The default property value
        :returns: Template that is interpolated by the JS widget with the
                  mapped values found in records
        """
        # check if the new `display_template` property is set
        prop = getattr(self, "display_template", None)
        if prop is not None:
            return prop
        return default

    def get_value(self, context, field, value=None):
        """Extract the value from the request or get it from the field

        :param context: The current context of the field
        :param field: The current field of the widget
        :param value: The current set value
        :returns: List of UIDs
        """
        # the value might come from the request, e.g. on object creation
        if api.is_string(value):
            value = filter(None, value.split("\r\n"))
        # we handle always lists in the templates
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            value = [value]
        return value

    def get_render_data(self, context, field, reference, template):
        """Provides the needed data to render the display template

        :returns: Dictionary with data needed to render the display template
        """
        if not reference:
            return {}

        return {
            "uid": "",
            "url": "",
            "Title": reference,
            "Description": "",
            "review_state": "active",
        }

    def render_reference(self, context, field, reference):
        """Returns a rendered HTML element for the reference
        """
        display_template = self.get_display_template(context, field, reference)
        template = string.Template(display_template)
        try:
            data = self.get_render_data(
                context, field, reference, display_template)
        except ValueError as e:
            # Current user might not have privileges to view this object
            logger.error(e.message)
            return ""

        if not data:
            return ""

        return template.safe_substitute(data)


registerWidget(QuerySelectWidget, title="QuerySelectWidget")
