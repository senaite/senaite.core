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

import six
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import StringWidget
from Products.CMFPlone.utils import base_hasattr
from senaite.core.browser.widgets.referencewidget_search import \
    IReferenceWidgetDataProvider
from zope.component import getAdapters

DEFAULT_SEARCH_CATALOG = "uid_catalog"
DISPLAY_TEMPLATE = "<a href='${url}' _target='blank'>${title}</a>"
IGNORE_COLUMNS = ["UID"]


class ReferenceWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        "macro": "senaite_widgets/uidreferencewidget",

        # NEW PROPERTIES
        "query": {},
        "limit": 5,
        "catalog": None,
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
        "results_table_width": "500px",

        # BBB: OLD PROPERTIES
        "url": "referencewidget_search",
        "catalog_name": "portal_catalog",
        # base_query can be a dict or a callable returning a dict
        "base_query": {},
        # columns to display in the search dropdown
        "colModel": [
            {"columnName": "Title", "width": "30", "label": _(
                "Title"), "align": "left"},
            {"columnName": "Description", "width": "70", "label": _(
                "Description"), "align": "left"},
            # UID is required in colModel
            {"columnName": "UID", "hidden": True},
        ],
        "ui_item": "Title",
        "search_fields": ("Title",),
        "discard_empty": [],
        "popup_width": "550px",
        "showOn": False,
        "searchIcon": True,
        "minLength": "0",
        "delay": "500",
        "resetButton": False,
        "sord": "asc",
        "sidx": "Title",
        "force_all": False,
        "portal_types": {},
    })

    def get_input_widget_attributes(self, context, field, value):
        """Return input widget attributes for the ReactJS component

        This method get called from the page template to populate the
        attributes that are used by the ReactJS widget component.

        :param context: The current context of the field
        :param field: The current field of the widget
        :param value: The curent field value (list of UIDs)
        """
        uids = self.get_value(context, field, value)
        attributes = {
            "data-id": field.getName(),
            "data-name": field.getName(),
            "data-values": uids,
            "data-records": dict(zip(uids, map(
                lambda uid: self.get_ref_data(context, field, uid), uids))),
            "data-value_key": getattr(self, "value_key", "uid"),
            "data-api_url": getattr(self, "url", "referencewidget_search"),
            "data-query": getattr(self, "query", {}),
            "data-catalog": getattr(self, "catalog", "portal_catalog"),
            "data-search_index": getattr(self, "search_index", "Title"),
            "data-search_wildcard": getattr(self, "search_wildcard", True),
            "data-allow_user_value": getattr(self, "allow_user_value", False),
            "data-columns": getattr(self, "columns", []),
            "data-display_template": getattr(
                self, "display_template", DISPLAY_TEMPLATE),
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
        following naming convention:

            <fieldname>_<propertyname>

        If an attribute or method is found, this value will be returned,
        otherwise the lookup will return the default value

        :param name: The name of a method to lookup
        :param context: The current context of the field
        :param field: The current field of the widget
        :param default: The default property value for the given name
        :returns: New value for the named property
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

        # BBB: call custom getter to map old widget properties
        key = name.replace("data-", "", 1)
        getter = "get_{}".format(key)
        method = getattr(self, getter, None)
        if callable(method):
            return method(context, field, default=None)

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
        # ensure the search path does not contain already the url
        search_path = self.url.split(url)[-1]
        # return the absolute search url
        return "/".join([url, search_path])

    def get_multi_valued(self, context, field, default=None):
        """Lookup if the field is single or multi valued

        :param context: The current context of the field
        :param field: The current field of the widget
        :param default: The default property value
        :returns: True if the field is multi valued, otherwise False
        """
        multi_valued = getattr(field, "multiValued", None)
        if multi_valued is None:
            return default
        return multi_valued

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

        # BBB: ui_item
        ui_item = getattr(self, "ui_item", None),
        if ui_item is not None:
            return "<a href='${url}' _target='blank'>${%s}</a>" % ui_item

        return default

    def get_catalog(self, context, field, default=None):
        """Lookup the catalog to query

        :param context: The current context of the field
        :param field: The current field of the widget
        :param default: The default property value
        :returns: Catalog name to query
        """
        # check if the new `catalog` property is set
        prop = getattr(self, "catalog", None)
        if prop is not None:
            return prop

        # BBB: catalog_name
        catalog_name = getattr(self, "catalog_name", None),

        if catalog_name is None:
            return DEFAULT_SEARCH_CATALOG
        return catalog_name

    def get_query(self, context, field, default=None):
        """Lookup the catalog query

        :param context: The current context of the field
        :param field: The current field of the widget
        :param default: The default property value
        :returns: Base catalog query
        """
        prop = getattr(self, "query", None)
        if prop:
            return prop

        base_query = getattr(self, "base_query", {})

        # extend portal_type filter
        allowed_types = getattr(field, "allowed_types", None)
        allowed_types_method = getattr(field, "allowed_types_method", None)
        if allowed_types_method:
            meth = getattr(context, allowed_types_method)
            allowed_types = meth(field)

        if api.is_string(allowed_types):
            allowed_types = [allowed_types]

        base_query["portal_type"] = list(allowed_types)

        return base_query

    def get_columns(self, context, field, default=None):
        """Lookup the columns to show in the results popup

        :param context: The current context of the field
        :param field: The current field of the widget
        :param default: The default property value
        :returns: List column records to display
        """
        prop = getattr(self, "columns", None)
        if prop is not None:
            return prop

        # BBB: colModel
        col_model = getattr(self, "colModel", [])

        if not col_model:
            return default

        columns = []
        for col in col_model:
            name = col.get("columnName")
            # skip ignored columns
            if name in IGNORE_COLUMNS:
                continue
            columns.append({
                "name": name,
                "width": col.get("width", "50%"),
                "align": col.get("align", "left"),
                "label": col.get("label", ""),
            })
        return columns

    def get_search_index(self, context, field, default=None):
        """Lookup the search index for fulltext searches

        :param context: The current context of the field
        :param field: The current field of the widget
        :param default: The default property value
        :returns: ZCText compatible search index
        """
        prop = getattr(self, "search_index", None)
        if prop is not None:
            return prop

        # BBB: search_fields
        search_fields = getattr(self, "search_fields", [])
        if not isinstance(search_fields, (tuple, list)):
            search_fields = filter(None, [search_fields])
        if len(search_fields) > 0:
            return search_fields[0]

        return default

    def get_value(self, context, field, value=None):
        """Extract the value from the request or get it from the field

        :param context: The current context of the field
        :param field: The current field of the widget
        :param value: The current set value
        :returns: List of UIDs
        """
        # the value might come from the request, e.g. on object creation
        if isinstance(value, six.string_types):
            value = filter(None, value.split("\r\n"))
        # we handle always lists in the templates
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            value = [value]
        return map(api.get_uid, value)

    def get_ref_data(self, context, field, uid):
        """Extract the data for the ference item

        :param brain: ZCatalog Brain Object
        :returns: Dictionary with extracted attributes
        """
        data = {}
        for name, adapter in getAdapters(
                (context, api.get_request()), IReferenceWidgetDataProvider):
            data.update(adapter.to_dict(uid, data=dict(data)))
        return data

    def render_reference(self, context, field, uid):
        """Returns a rendered HTML element for the reference
        """
        template = string.Template(
            self.get_display_template(context, field, uid))
        try:
            data = self.get_ref_data(context, field, uid)
        except ValueError as e:
            # Current user might not have privileges to view this object
            logger.error(e.message)
            return ""

        return template.safe_substitute(data)


registerWidget(ReferenceWidget, title="Reference Widget")
