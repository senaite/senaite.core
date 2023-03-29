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

import six

from bika.lims import api
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

_marker = object


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

    def lookup(self, name, field, context, default=None):
        """Check if the context has an override for the given named property

        The context can either define an attribute or a method with the
        following naming convention:

            <fieldname>_<propertyname>

        If an attribute or method is found, this value will be returned,
        otherwise the lookup will return the default value
        """

        # check if the current context defines an attribute or method for the
        # given property
        key = "{}_{}".format(field.getName(), name)
        if base_hasattr(context, key):
            attr = getattr(context, key, default)
            if callable(attr):
                # call the context method with additional information
                attr = attr(name=name,
                            widget=self,
                            field=field,
                            context=context,
                            default=default)
            return attr

        # return the widget attribute
        return getattr(self, name, default)

    def get_value(self):
        """Extract the value from the request or get it from the field
        """
        # get the processed value from the `update` method
        value = self.value
        # the value might come from the request, e.g. on object creation
        if isinstance(value, six.string_types):
            value = IDataConverter(self).toFieldValue(value)
        # we handle always lists in the templates
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            value = [value]
        return value

    def get_input_widget_attributes(self):
        """Return input widget attributes for the ReactJS component
        """
        context = self.get_context()
        values = self.get_value()
        attributes = {
            "data-id": self.id,
            "data-name": self.name,
            "data-values": values,
            "data-value_key": getattr(self, "value_key", "uid"),
            "data-api_url": self.get_api_url(),
            "data-query": getattr(self, "query", {}),
            "data-catalog": getattr(self, "catalog", "portal_catalog"),
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
                self, "hide_user_input_after_select", False),
        }

        for key, value in attributes.items():
            # lookup attributes for overrides
            value = self.lookup(key, self.field, context, default=value)
            # convert all attributes to JSON
            attributes[key] = json.dumps(value)

        return attributes

    def get_api_url(self):
        """JSON API URL to use for this widget
        """
        portal = api.get_portal()
        portal_url = api.get_url(portal)
        api_url = "{}/@@API/senaite/v1".format(portal_url)
        return api_url


@adapter(IField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def QuerySelectWidgetFactory(field, request):
    """Widget factory
    """
    return FieldWidget(field, QuerySelectWidget(request))
