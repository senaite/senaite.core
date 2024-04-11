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

import re

from bika.lims import api
from bika.lims import logger
from bika.lims import senaiteMessageFactory as _
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IUIDReferenceField
from senaite.core.z3cform.interfaces import IUIDReferenceWidget
from senaite.core.z3cform.widgets.queryselect import QuerySelectDataConverter
from senaite.core.z3cform.widgets.queryselect import QuerySelectWidget
from z3c.form import interfaces
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer

DISPLAY_TEMPLATE = "<a href='${url}' _target='blank'>${Title}</a>"


@adapter(IUIDReferenceField, interfaces.IWidget)
class UIDReferenceDataConverter(QuerySelectDataConverter):
    """Converts the raw field data for widget/field usage
    """


@implementer(IUIDReferenceWidget)
class UIDReferenceWidget(QuerySelectWidget):
    """Senaite UID reference widget
    """
    klass = u"senaite-uidreference-widget-input"

    def get_value_key(self, context, field, default=None):
        """Returns the data key that should be set as the value
        """
        return "uid"

    def get_value_query_index(self, context, field, default=None):
        """Index that needs to be queried to fetch the data for the current values
        """
        return "UID"

    def get_query(self, context, field, default=None):
        """Ensure the allowed types are in the query

        NOTE: This method is called from `self.lookup` as the last resort if no
              custom query method or callable was found for this widget.
        """
        query = getattr(self, "query", {})
        if not isinstance(query, dict):
            logger.error(
                "Invalid query provided for field '%s'" % field.getName())
            query = {}

        # ensure the query is always limited to the allowed types
        allowed_types = field.get_allowed_types()
        query["portal_type"] = list(allowed_types)

        return query

    def get_columns(self, context, field, default=None):
        """Ensure default columns if not set

        NOTE: This method is called from `self.lookup` as the last resort if no
              custom columns method or callable was found for this widget.
        """
        columns = getattr(self, "columns", [])
        if not isinstance(columns, list):
            logger.error(
                "Invalid columns provided for field '%s'" % field.getName())
            columns = []

        # Provide default columns
        if not columns:
            columns = [
                {"name": "Title", "label": _("Title")},
                {"name": "Description", "label": _("Description")},
            ]

        return columns

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
        # just to be sure (paranoid)
        return [uid for uid in value if api.is_uid(uid)]

    def get_render_data(self, context, field, uid):
        """Provides the needed data to render the display template from the UID

        :returns: Dictionary with data needed to render the display template
        """
        regex = r"\{(.*?)\}"
        context = self.get_context()
        template = self.get_display_template(context, self.field)
        names = re.findall(regex, template)

        try:
            obj = api.get_object(uid)
        except api.APIError:
            logger.error("No object found for field '{}' with UID '{}'".format(
                field.getName(), uid))
            return {}

        data = {
            "uid": api.get_uid(obj),
            "url": api.get_url(obj),
            "Title": api.get_title(obj) or api.get_id(obj),
            "Description": api.get_description(obj),
        }
        for name in names:
            if name not in data:
                value = getattr(obj, name, None)
                if callable(value):
                    value = value()
                data[name] = value

        return data


@adapter(IUIDReferenceField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def UIDReferenceWidgetFactory(field, request):
    """Widget factory for UIDReferenceField
    """
    return FieldWidget(field, UIDReferenceWidget(request))
