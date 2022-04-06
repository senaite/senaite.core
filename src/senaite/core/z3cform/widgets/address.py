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
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IAddressField
from senaite.core.z3cform.interfaces import IAddressWidget
from z3c.form.browser.widget import HTMLFormElement
from z3c.form.converter import FieldDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import implementer


@adapter(IAddressField, IWidget)
class AddressDataConverter(FieldDataConverter):
    """Value conversion between field and widget
    """
    def to_list_of_dicts(self, value):
        if not isinstance(value, list):
            value = [value]
        value = filter(None, value)
        return map(self.to_dict, value)

    def to_dict(self, value):
        if not isinstance(value, dict):
            return {}
        return value

    def toWidgetValue(self, value):
        """Returns the field value with encoded string
        """
        return self.to_list_of_dicts(value)

    def toFieldValue(self, value):
        """Converts from widget value to safe_unicode
        """
        return self.to_list_of_dicts(value)


@implementer(IAddressWidget)
class AddressWidget(HTMLFormElement, Widget):
    """SENAITE Address Widget
    """
    klass = u"address-widget"

    # Address html format for display. Wildcards accepted: {type}, {address},
    # {zip}, {district}, {city}, {state}, {country}. Use '<br/>' for newlines
    address_format = ""

    def get_address_format(self):
        """Returns the format for displaying the address
        """
        if self.address_format:
            return self.address_format
        lines = [
            "<strong>{type}</strong>",
            "{address}",
            "{zip} {district} {city}",
            "{state}",
            "{country}"
        ]
        return "<br/>".join(lines)

    def get_formatted_address(self, address):
        """Returns the address formatted in html
        """
        address_format = self.get_address_format()
        lines = address_format.split("<br/>")
        values = map(lambda line: line.format(**address), lines)
        values = filter(None, values)
        return "<br/>".join(values)

    def get_input_widget_attributes(self):
        """Return input widget attributes for the ReactJS component
        """
        attributes = {
            "data-id": self.id,
            "data-name": self.name,
            "data-info": self.value,
            "data-disabled": self.disabled or False,
        }
        for key, value in attributes.items():
            attributes[key] = json.dumps(value)

        return attributes


@adapter(IAddressField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def AddressWidgetFactory(field, request):
    """Widget factory for Address Widget
    """
    return FieldWidget(field, AddressWidget(request))
