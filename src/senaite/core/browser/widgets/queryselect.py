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

from AccessControl import ClassSecurityInfo
from bika.lims import api
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFPlone.utils import base_hasattr

_marker = object


class QuerySelectWidget(TypesWidget):
    """AT Backport of Dexterity Queryselect Widget

    https://github.com/senaite/senaite.core/pull/2177
    """
    security = ClassSecurityInfo()
    _properties = TypesWidget._properties.copy()
    _properties.update({
        "macro": "senaite_widgets/queryselectwidget",
        "query": {},
        "limit": 25,
        "catalog": "portal_catalog",
        "api_url": None,
        "disabled": False,
        "readonly": False,
        "multi_valued": False,
        "allow_user_value": False,
        "search_wildcard": True,
        "value_key": "uid",
        "padding": 3,
        "display_template": None,
        "hide_input_after_select": False,
    })

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

    def to_value(self, value):
        """Extract the value from the request or get it from the field
        """
        # the value might come from the request, e.g. on object creation
        if isinstance(value, six.string_types):
            value = filter(None, value.split("\r\n"))
        # we handle always lists in the templates
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            value = [value]
        return value

    def get_api_url(self, field, context):
        """JSON API URL to use for this widget
        """
        portal = api.get_portal()
        portal_url = api.get_url(portal)
        api_url = self.lookup("api_url", field, context)
        if not api_url:
            api_url = "{}/@@API/senaite/v1".format(portal_url)
        return api_url

    def get_input_widget_attributes(self, context, field, value):
        """Return input widget attributes for the ReactJS component
        """
        attributes = {
            "data-id": field.getName(),
            "data-name": field.getName(),
            "data-api_url": self.get_api_url(field, context),
            "data-catalog": self.catalog,
            "data-query": self.query,
            "data-values": self.to_value(value),
            "data-value_key": self.value_key,
            "data-columns": self.columns,
            "data-multi_valued": self.multi_valued,
            "data-search_index": self.search_index,
            "data-search_wildcard": self.search_wildcard,
            "data-display_template": self.display_template,
            "data-limit": self.limit,
            "data-allow_user_value": self.allow_user_value,
            "data-hide_input_after_select": self.hide_input_after_select,
        }

        for key, value in attributes.items():
            # lookup attributes for overrides
            value = self.lookup(key, field, context, default=value)
            # convert all attributes to JSON
            attributes[key] = json.dumps(value)

        return attributes


registerWidget(QuerySelectWidget, title="QuerySelectWidget")
