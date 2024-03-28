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
from Products.CMFPlone.utils import base_hasattr
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.z3cform.interfaces import IQuerySelectWidget
from senaite.core.z3cform.widgets.basewidget import BaseWidget
from z3c.form.browser import widget
from z3c.form.converter import TextLinesConverter
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IField
from zope.schema.interfaces import ISequence

# See IReferenceWidgetDataProvider for provided object data
DISPLAY_TEMPLATE = "<div>${Title}</div>"

# Search index placeholder for dynamic lookup by the search endpoint
SEARCH_INDEX_MARKER = "__search__"


@adapter(ISequence, IQuerySelectWidget)
class QuerySelectDataConverter(TextLinesConverter):
    """Converter for multi valued List fields
    """
    def toWidgetValue(self, value):
        """Return the value w/o changes

        Note:

        All widget templates use the `get_value` method,
        which ensures a list of UIDs.

        However, `toWidgetValue` is called by `widget.update()` implicitly for
        `self.value`, which is then used by the `get_value` method again.
        """
        return value

    def toFieldValue(self, value):
        """Converts a unicode string to a list of UIDs
        """
        if api.is_list(value):
            value = "\r\n".join(value)
        elif api.is_string(value):
            # remove any blank lines at the end
            value = value.rstrip("\r\n")
        else:
            value = ""

        return super(QuerySelectDataConverter, self).toFieldValue(value)


@implementer_only(IQuerySelectWidget)
class QuerySelectWidget(widget.HTMLInputWidget, BaseWidget):
    """A widget to select one or more items from catalog search
    """
    klass = u"senaite-queryselect-widget-input"

    def update(self):
        super(QuerySelectWidget, self).update()
        widget.addFieldClass(self)

    def get_input_widget_attributes(self):
        """Return input widget attributes for the ReactJS component

        This method get called from the page template to populate the
        attributes that are used by the ReactJS widget component.
        """
        context = self.get_context()
        values = self.get_value()
        field = self.field

        attributes = {
            "data-id": self.id,
            "data-name": self.name,
            "data-values": values,
            "data-records": dict(zip(values, map(
                lambda ref: self.get_render_data(
                    context, field, ref), values))),
            "data-value_key": getattr(self, "value_key", "title"),
            "data-value_query_index": getattr(
                self, "value_query_index", "title"),
            "data-api_url": getattr(self, "api_url", "referencewidget_search"),
            "data-query": getattr(self, "query", {}),
            "data-catalog": getattr(self, "catalog", None),
            "data-search_index": getattr(
                self, "search_index", SEARCH_INDEX_MARKER),
            "data-search_wildcard": getattr(self, "search_wildcard", True),
            "data-allow_user_value": getattr(self, "allow_user_value", False),
            "data-columns": getattr(self, "columns", []),
            "data-display_template": getattr(self, "display_template", None),
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

            get_widget_<fieldname>_<propertyname>

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

        # NOTE: The temporary context created by `self.get_context` if we are
        #       in the ++add++ creation form for Dexterity contents exists only
        #       for the current request and will be gone after response!
        #       Therefore, the search view called later will result in a 404!
        if api.is_temporary(context):
            portal_type = self.get_portal_type()
            parent_url = api.get_url(api.get_parent(context))
            # provide a dynamically created context for the search view to call
            # the right search adapters.
            url = "{}/@@temporary_context/{}".format(parent_url, portal_type)

        # get the API URL
        api_url = getattr(self, "api_url", default)
        # ensure the search path does not contain already the url
        search_path = api_url.split(url)[-1]
        # return the absolute search url
        return "/".join([url, search_path])

    def get_display_template(self, context, field, default=None):
        """Return the display template to use
        """
        template = getattr(self, "display_template", None)
        if template is not None:
            return template
        return DISPLAY_TEMPLATE

    def get_multi_valued(self, context, field, default=None):
        """Returns if the field is multi valued or not
        """
        return getattr(self.field, "multi_valued", default)

    def get_catalog(self, context, field, default=None):
        """Lookup the catalog to query

        :param context: The current context of the field
        :param field: The current field of the widget
        :param default: The default property value
        :returns: Catalog name to query
        """
        # check if the new `catalog` property is set
        catalog_name = getattr(self, "catalog", None)

        if catalog_name is None:
            # try to lookup the catalog for the given object
            catalogs = api.get_catalogs_for(context)
            # function always returns at least one catalog object
            catalog_name = catalogs[0].getId()

        return catalog_name

    def get_value(self):
        """Extract the value from the request or get it from the field
        """
        # get the processed value from the `update` method
        value = self.value
        # the value might come from the request, e.g. on object creation
        if api.is_string(value):
            value = IDataConverter(self).toFieldValue(value)
        # we handle always lists in the templates
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            value = [value]
        return value

    def get_render_data(self, context, field, reference):
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

    def render_reference(self, reference):
        """Returns a rendered HTML element for the reference
        """
        context = self.get_context()
        field = self.field
        display_template = self.get_display_template(context, field)
        template = string.Template(display_template)
        try:
            data = self.get_render_data(context, field, reference)
        except ValueError as e:
            # Current user might not have privileges to view this object
            logger.error(e.message)
            return ""

        if not data:
            return ""

        return template.safe_substitute(data)


@adapter(IField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def QuerySelectWidgetFactory(field, request):
    """Widget factory
    """
    return FieldWidget(field, QuerySelectWidget(request))
