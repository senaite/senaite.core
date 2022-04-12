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
from senaite.core.api import geo
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

from bika.lims import api


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
    klass = u"senaite-address-widget"

    # Address html format for display. Wildcards accepted: {type}, {address},
    # {zip}, {city}, {district}, {subdivision1}, {subdivision2}, {country}.
    # Use '<br/>' for newlines
    address_format = ""

    def get_address_format(self):
        """Returns the format for displaying the address
        """
        if self.address_format:
            return self.address_format
        lines = [
            "<strong>{type}</strong>",
            "{address}",
            "{zip} {city}",
            "{subdivision2}",
            "{subdivision1}",
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

    def get_geographical_hierarchy(self):
        """Returns a dict with geographical information as follows:

            {<country_name_1>: {
                <subdivision1_name_1>: [
                    <subdivision2_name_1>,
                    ...
                    <subdivision2_name_n>,
                ],
                ...
                <subdivision1_name_n>: [..]
                },
            <country_name_2>: {
                ...
            }

        Available 2-level subdivisions for each country are only considered for
        those countries selected in current addresses
        """

        # Initialize a dict with countries names as keys and None as values
        countries = map(lambda c: c.name, geo.get_countries())
        countries = dict.fromkeys(countries)

        # Fill the dict with geo information for selected countries only
        for item in self.value:
            country = item.get("country")
            subdivision1 = item.get("subdivision1")

            # Init a dict with 1st level subdivision names as keys
            subdivisions1 = geo.get_subdivisions(country, default=[])
            subdivisions1 = map(lambda sub: sub.name, subdivisions1)
            subdivisions1 = dict.fromkeys(subdivisions1)

            # Fill with 2nd level subdivision names
            subdivisions2 = geo.get_subdivisions(subdivision1, default=[])
            subdivisions2 = map(lambda sub: sub.name, subdivisions2)
            subdivisions1[subdivision1] = subdivisions2

            # Set the value to the geomap
            countries[country] = subdivisions1

        return countries

    def get_input_widget_attributes(self):
        """Return input widget attributes for the ReactJS component
        """
        attributes = {
            "data-id": self.id,
            "data-uid": api.get_uid(self.context),
            "data-geography": self.get_geographical_hierarchy(),
            "data-name": self.name,
            "data-portal_url": api.get_url(api.get_portal()),
            "data-items": self.value,
            "data-title": self.title,
            "data-class": self.klass,
            "data-style": self.style,
            "data-disabled": self.disabled or False,
        }

        # convert all attributes to JSON
        for key, value in attributes.items():
            attributes[key] = json.dumps(value)

        return attributes


@adapter(IAddressField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def AddressWidgetFactory(field, request):
    """Widget factory for Address Widget
    """
    return FieldWidget(field, AddressWidget(request))
