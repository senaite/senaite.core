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

import re
import string

from bika.lims import api
from bika.lims import logger
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
DEFAULT_SEARCH_CATALOG = "uid_catalog"


@adapter(IUIDReferenceField, interfaces.IWidget)
class UIDReferenceDataConverter(QuerySelectDataConverter):
    """Converts the raw field data for widget/field usage
    """


@implementer(IUIDReferenceWidget)
class UIDReferenceWidget(QuerySelectWidget):
    """Senaite UID reference widget
    """
    klass = u"senaite-uidreference-widget-input"

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
        return map(api.get_uid, value)

    def get_render_data(self, uid):
        """Provides the needed data to render the display template from the UID

        :returns: Dictionary with data needed to render the display template
        """
        regex = r"\{(.*?)\}"
        template = getattr(self, "display_template", DISPLAY_TEMPLATE)
        names = re.findall(regex, template)

        obj = api.get_object(uid)
        data = {
            "uid": api.get_uid(obj),
            "url": api.get_url(obj),
            "Title": api.get_title(obj),
            "Description": api.get_description(obj),
        }
        for name in names:
            if name not in data:
                value = getattr(obj, name, None)
                if callable(value):
                    value = value()
                data[name] = value

        return data

    def render_reference(self, reference):
        """Returns a rendered HTML element for the reference
        """
        display_template = getattr(self, "display_template", DISPLAY_TEMPLATE)
        template = string.Template(display_template)
        try:
            data = self.get_render_data(reference)
        except ValueError as e:
            # Current user might not have privileges to view this object
            logger.error(e.message)
            return ""

        return template.safe_substitute(data)


@adapter(IUIDReferenceField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def UIDReferenceWidgetFactory(field, request):
    """Widget factory for UIDReferenceField
    """
    return FieldWidget(field, UIDReferenceWidget(request))
