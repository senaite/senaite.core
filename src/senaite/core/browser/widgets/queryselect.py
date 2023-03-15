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
from AccessControl import ClassSecurityInfo
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

    def attr(self, context, name, default=None):
        """Get the named attribute of the widget or from the context
        """
        value = getattr(self, name, _marker)
        if value is _marker:
            return default
        if isinstance(value, six.string_types):
            if base_hasattr(context, value):
                attr = getattr(context, value)
                if callable(attr):
                    attr = attr()
                if attr:
                    value = attr
        return value

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

    def get_api_url(self, context):
        """JSON API URL to use for this widget
        """
        portal = api.get_portal()
        portal_url = api.get_url(portal)
        api_url = self.attr(context, "api_url")
        if not api_url:
            api_url = "{}/@@API/senaite/v1".format(portal_url)
        return api_url

    def get_input_widget_attributes(self, context, field, value):
        """Return input widget attributes for the ReactJS component
        """
        attributes = {
            "data-id": field.getName(),
            "data-name": field.getName(),
            "data-values": self.to_value(value),
            "data-value_key": self.attr(context, "value_key"),
            "data-columns": self.attr(context, "columns"),
            "data-query": self.attr(context, "query"),
            "data-multi_valued": self.attr(context, "multi_valued"),
            "data-api_url": self.get_api_url(context),
            "data-search_index": self.attr(context, "search_index"),
            "data-search_wildcard": self.attr(context, "search_wildcard"),
            "data-limit": self.attr(context, "limit"),
            "data-catalog": self.attr(context, "catalog"),
            "data-allow_user_value": self.attr(context, "allow_user_value"),
            "data-hide_input_after_select": self.attr(
                context, "hide_input_after_select"),
        }

        # convert all attributes to JSON
        for key, value in attributes.items():
            attributes[key] = json.dumps(value)

        return attributes


registerWidget(QuerySelectWidget, title="QuerySelectWidget")
