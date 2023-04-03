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
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IReferenceWidgetVocabulary
from bika.lims.utils import to_unicode as _u
from plone import protect
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import StringWidget
from Products.CMFPlone.utils import base_hasattr
from senaite.app.supermodel.model import SuperModel
from zope.component import getAdapters
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

DISPLAY_TEMPLATE = "<a href='${url}' _target='blank'>${title}</a>"


class ReferenceWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        "macro": "senaite_widgets/uidreferencewidget",


        # OLD PROPERTIES BELOW THIS LINE
        "url": "referencewidget_search",
        "catalog_name": "portal_catalog",
        # base_query can be a dict or a callable returning a dict
        "base_query": {},
        # This will be faster if the columnNames are catalog indexes
        "colModel": [
            {"columnName": "Title", "width": "30", "label": _(
                "Title"), "align": "left"},
            {"columnName": "Description", "width": "70", "label": _(
                "Description"), "align": "left"},
            # UID is required in colModel
            {"columnName": "UID", "hidden": True},
        ],
        # Default field to put back into input elements
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
        """
        attributes = {
            "data-id": field.getName(),
            "data-name": field.getName(),
            "data-values": self.to_value(value),
            "data-value_key": getattr(self, "value_key", "uid"),
            "data-api_url": "referencewidget_search",
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
                self, "hide_user_input_after_select", False),
        }

        for key, value in attributes.items():
            # lookup attributes for overrides
            value = self.lookup(key, context, field, default=value)
            # convert all attributes to JSON
            attributes[key] = json.dumps(value)

        return attributes

    def get_api_url(self, context, field, default=None):
        """JSON API URL to use for this widget
        """
        portal = api.get_portal()
        portal_url = api.get_url(portal)
        api_url = "{}/referencewidget_search".format(portal_url)
        return api_url

    def lookup(self, name, context, field, default=None):
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

        # BBB: call custom getter to map old widget properties
        key = name.replace("data-", "", 1)
        getter = "get_{}".format(key)
        method = getattr(self, getter, None)
        if callable(method):
            return method(field, context, default=None)

        # return the widget attribute
        return getattr(self, name, default)

    def get_display_template(self, field, context, default=None):
        """Lookup the display template
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

    def get_catalog(self, field, context, default=None):
        """Lookup the catalog to query
        """
        # check if the new `catalog` property is set
        prop = getattr(self, "catalog", None)
        if prop is not None:
            return prop

        # BBB: catalog_name
        return getattr(self, "catalog_name", default),

    def get_query(self, field, context, default=None):
        """Lookup the catalog query
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

    def get_columns(self, field, context, default=None):
        """Lookup the columns to show in the results popup
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
            columns.append({
                "name": col.get("columnName", ""),
                "width": col.get("width", ""),
                "align": col.get("align", "left"),
                "label": col.get("label", ""),
            })
        return columns

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

    def get_obj_info(self, uid):
        """Returns a dictionary with the object info
        """
        model = SuperModel(uid)
        obj_info = model.to_dict()
        obj_info["uid"] = uid
        obj_info["url"] = api.get_url(model)

        # extend the brain metadata as well
        for attr in model.brain.schema():
            obj_info[attr] = getattr(model.brain, attr, "")

        return obj_info

    def render_reference(self, context, field, uid):
        """Returns a rendered HTML element for the reference
        """
        template = string.Template(
            self.get_display_template(context, field, uid))
        try:
            obj_info = self.get_obj_info(uid)
        except ValueError as e:
            # Current user might not have privileges to view this object
            logger.error(e.message)
            return ""

        return template.safe_substitute(obj_info)

    ###
    # OLD STUFF BELOW THIS LINE
    ###
    def get_search_url(self, context):
        """Prepare an absolute search url for the combobox
        """
        # ensure we have an absolute url for the current context
        url = api.get_url(context)
        # normalize portal factory urls
        url = url.split("portal_factory")[0]
        # ensure the search path does not contain already the url
        search_path = self.url.split(url)[-1]
        # return the absolute search url
        return "/".join([url, search_path])

    def get_combogrid_options(self, context, fieldName):
        colModel = self.colModel
        if "UID" not in [x["columnName"] for x in colModel]:
            colModel.append({"columnName": "UID", "hidden": True})

        options = {
            "url": self.get_search_url(context),
            "colModel": colModel,
            "showOn": self.showOn,
            "width": self.popup_width,
            "sord": self.sord,
            "sidx": self.sidx,
            "force_all": self.force_all,
            "search_fields": self.search_fields,
            "discard_empty": self.discard_empty,
            "minLength": self.minLength,
            "resetButton": self.resetButton,
            "searchIcon": self.searchIcon,
            "delay": self.delay,
        }
        return json.dumps(options)

    def get_base_query(self, context, fieldName):
        base_query = self.base_query
        if callable(base_query):
            try:
                base_query = base_query(context, self, fieldName)
            except TypeError:
                base_query = base_query()
        if base_query and isinstance(base_query, six.string_types):
            base_query = json.loads(base_query)

        # portal_type: use field allowed types
        field = context.Schema().getField(fieldName)
        allowed_types = getattr(field, "allowed_types", None)
        allowed_types_method = getattr(field, "allowed_types_method", None)
        if allowed_types_method:
            meth = getattr(context, allowed_types_method)
            allowed_types = meth(field)
        # If field has no allowed_types defined, use widget"s portal_type prop
        base_query["portal_type"] = allowed_types \
            if allowed_types \
            else self.portal_types

        return json.dumps(base_query)

    def initial_uid_field_value(self, value):
        if type(value) in (list, tuple):
            ret = ",".join([v.UID() for v in value])
        elif isinstance(value, six.string_types):
            ret = value
        else:
            ret = value.UID() if value else value
        return ret


registerWidget(ReferenceWidget, title="Reference Widget")


@implementer(IPublishTraverse)
class ajaxReferenceWidgetSearch(BrowserView):
    """ Source for jquery combo dropdown box
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        """Called before __call__ for each path name and allows to dispatch
        subpaths to methods
        """
        self.traverse_subpath.append(name)
        return self

    @property
    def num_page(self):
        """Returns the number of page to render
        """
        return api.to_int(self.request.get("page", None), default=1)

    @property
    def num_rows_page(self):
        """Returns the number of rows per page to render
        """
        return api.to_int(self.request.get("rows", None), default=10)

    def get_field_names(self):
        """Return the field names to get values for
        """
        col_model = self.request.get("colModel", None)
        if not col_model:
            return ["UID",]

        names = []
        col_model = json.loads(_u(col_model))
        if isinstance(col_model, (list, tuple)):
            names = map(lambda c: c.get("columnName", "").strip(), col_model)

        # UID is used by reference widget to know the object that the user
        # selected from the popup list
        if "UID" not in names:
            names.append("UID")

        return filter(None, names)

    def get_data_record(self, brain, field_names):
        """Returns a dict with the column values for the given brain
        """
        record = {}
        model = None

        for field_name in field_names:
            # First try to get the value directly from the brain
            value = getattr(brain, field_name, None)

            # No metadata for this column name
            if value is None:
                logger.warn("Not a metadata field: {}".format(field_name))
                model = model or SuperModel(brain)
                value = model.get(field_name, None)
                if callable(value):
                    value = value()

            # '&nbsp;' instead of '' because empty div fields don't render
            # correctly in combo results table
            record[field_name] = value or "&nbsp;"

        return record

    def search(self):
        """Returns the list of brains that match with the request criteria
        """
        brains = []
        # TODO Legacy
        for name, adapter in getAdapters((self.context, self.request),
                                         IReferenceWidgetVocabulary):
            brains.extend(adapter())
        return brains

    def to_data_rows(self, brains):
        """Returns a list of dictionaries representing the values of each brain
        """
        fields = self.get_field_names()
        return map(lambda brain: self.get_data_record(brain, fields), brains)

    def to_json_payload(self, data_rows):
        """Returns the json payload
        """
        num_rows = len(data_rows)
        num_page = self.num_page
        num_rows_page = self.num_rows_page

        pages = num_rows / num_rows_page
        pages += divmod(num_rows, num_rows_page)[1] and 1 or 0
        start = (num_page - 1) * num_rows_page
        end = num_page * num_rows_page
        payload = {"page": num_page,
                   "total": pages,
                   "records": num_rows,
                   "rows": data_rows[start:end]}
        return json.dumps(payload)

    def __call__(self):
        protect.CheckAuthenticator(self.request)

        # Do the search
        brains = self.search()

        # Generate the data rows to display
        data_rows = self.to_data_rows(brains)

        # Return the payload
        return self.to_json_payload(data_rows)
