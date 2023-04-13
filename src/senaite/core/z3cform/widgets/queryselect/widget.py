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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
import string

from bika.lims import api
from bika.lims import logger
from plone.z3cform.fieldsets.interfaces import IDescriptiveGroup
from Products.CMFPlone.utils import base_hasattr
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.z3cform.interfaces import IQuerySelectWidget
from z3c.form.browser import widget
from z3c.form.converter import TextLinesConverter
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import ISubForm
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.component import getUtility
from zope.component.interfaces import IFactory
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IField
from zope.schema.interfaces import ISequence

# See IReferenceWidgetDataProvider for provided object data
DISPLAY_TEMPLATE = "<div>${Title}</div>"
DEFAULT_SEARCH_CATALOG = "uid_catalog"


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
        # remove any blank lines at the end
        value = value.rstrip("\r\n")
        return super(QuerySelectDataConverter, self).toFieldValue(value)


@implementer_only(IQuerySelectWidget)
class QuerySelectWidget(widget.HTMLInputWidget, Widget):
    """A widget to select one or more items from catalog search
    """
    klass = u"senaite-queryselect-widget-input"

    def update(self):
        super(QuerySelectWidget, self).update()
        widget.addFieldClass(self)

    def get_form(self):
        """Return the current form of the widget
        """
        form = self.form
        # form is a fieldset group
        if IDescriptiveGroup.providedBy(form):
            form = form.parentForm
        # form is a subform (e.g. DataGridFieldObjectSubForm)
        if ISubForm.providedBy(form):
            form = form.parentForm
        return form

    def get_context(self):
        """Get the current context

        NOTE: If we are in the ++add++ form, `self.context` is the container!
              Therefore, we create one here to have access to the methods.
        """
        schema_iface = self.field.interface
        if schema_iface and schema_iface.providedBy(self.context):
            return self.context

        # we might be in a subform, so try first to retrieve the object from
        # the base form itself first
        form = self.get_form()
        portal_type = getattr(form, "portal_type", None)
        context = getattr(form, "context", None)
        if api.is_object(context):
            if api.get_portal_type(context) == portal_type:
                return context

        # Hack alert!
        # we are in ++add++ form and have no context!
        # Create a temporary object to be able to access class methods
        if not portal_type:
            portal_type = api.get_portal_type(self.context)
        portal_types = api.get_tool("portal_types")
        fti = portal_types[portal_type]
        factory = getUtility(IFactory, fti.factory)
        context = factory("temporary")
        # hook into acquisition chain
        context = context.__of__(self.context)
        return context

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
                lambda ref: self.get_render_data(ref), values))),
            "data-value_key": getattr(self, "value_key", "title"),
            "data-value_query_index": getattr(
                self, "value_query_index", "title"),
            "data-api_url": getattr(self, "api_url", "referencewidget_search"),
            "data-query": getattr(self, "query", {}),
            "data-catalog": getattr(self, "catalog", DEFAULT_SEARCH_CATALOG),
            "data-search_index": getattr(self, "search_index", "Title"),
            "data-search_wildcard": getattr(self, "search_wildcard", True),
            "data-allow_user_value": getattr(self, "allow_user_value", False),
            "data-columns": getattr(self, "columns", []),
            "data-display_template": getattr(self, "display_template", None),
            "data-limit": getattr(self, "limit", 5),
            "data-multi_valued": getattr(self, "multi_valued", True),
            "data-disabled": getattr(self, "disabled", False),
            "data-readonly": getattr(self, "readonly", False),
            "data-hide_input_after_select": getattr(
                self, "hide_user_input_after_select", True),
        }

        for key, value in attributes.items():
            # lookup attributes for overrides
            value = self.lookup(key, context, field, default=value)
            # convert all attributes to JSON
            attributes[key] = json.dumps(value)

        return attributes

    def lookup(self, name, context, field, default=None):
        """Check if the context has an override for the given named property

        The context can either define an attribute or a method with the
        following naming convention (all lower case):

            get_<fieldname>_<propertyname>

        If an attribute or method is found, this value will be returned,
        otherwise the lookup will return the default value

        :param name: The name of a method to lookup
        :param context: The current context of the field
        :param field: The current field of the widget
        :param default: The default property value for the given name
        :returns: New value for the named property
        """
        # Remove the data prefix
        key = name.replace("data-", "", 1)
        # check if the current context defines an attribute or method for the
        # given property
        context_key = "get_{}_{}".format(field.getName(), key).lower()
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

        # BBB: call custom getter to map old widget properties
        getter = "get_{}".format(key)
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
        # get the URL
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

    def get_render_data(self, reference):
        """Provides the needed data to render the display template

        :returns: Dictionary with data needed to render the display template
        """
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
        display_template = self.get_display_template(context, self.field)
        template = string.Template(display_template)
        try:
            data = self.get_render_data(reference)
        except ValueError as e:
            # Current user might not have privileges to view this object
            logger.error(e.message)
            return ""

        return template.safe_substitute(data)


@adapter(IField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def QuerySelectWidgetFactory(field, request):
    """Widget factory
    """
    return FieldWidget(field, QuerySelectWidget(request))
