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
from bika.lims import logger
from senaite.core.locales import DISTRICTS
from senaite.core.locales import STATES

from bika.lims import api
from senaite.core.locales import COUNTRIES
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
    klass = u"senaite-address-widget"

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

    def get_countries_names(self):
        """Returns the list of names of available countries
        """
        countries = map(lambda country: country.get("Country"), COUNTRIES)
        countries = sorted(filter(None, countries))
        return countries

    def get_country_iso(self, name_or_iso):
        """Returns the iso for the country with the given name or iso
        """
        for country in COUNTRIES:
            if country.get("Country") == name_or_iso:
                return country.get("ISO")
            elif country.get("ISO") == name_or_iso:
                return name_or_iso
        return None

    def get_state_code(self, country, state):
        """Returns the code of the state from the country with given name or iso
        """
        iso = self.get_country_iso(country)
        for state_info in STATES:
            if iso != state_info[0]:
                continue
            if state in state_info:
                return state_info[1]
        return None

    def get_geographical_hierarchy(self):
        """Returns a dict with geographical information as follows:

            {<country_name_1>: {
                <state_name_1>: [
                    <district_name_1>,
                    ...
                    <district_name_n>,
                ],
                ...
                <state_name_n>: [..]
                },
            <country_name_2>: {
                ...
            }

        Available states and districts for each country are only considered for
        those countries selected in current addresses
        """

        # Initialize a dict with countries names as keys and None as values
        countries = self.get_countries_names()
        countries = dict.fromkeys(countries)

        # Fill the dict with geo information for selected countries only
        for item in self.value:
            country = item.get("country")

            # Initialize a dict with states names as keys and None as values
            states = self.get_states(country)
            states = map(lambda st: st[1], states)
            states = dict.fromkeys(states)

            # Fill the dict with geo information for selected state only
            state = item.get("state")
            states[state] = self.get_districts(country, state)

            # Set the value to the geomap
            countries[country] = states

        return countries

    def get_states(self, country):
        """Returns the states for the country with the given name or iso

        :param country: name or iso of the country
        :return: a list of tuples as (<state_code>, <state_name>)
        """
        iso = self.get_country_iso(country)
        states = filter(lambda state: state[0] == iso, STATES)
        return map(lambda state: (state[1], state[2]), states)

    def get_districts(self, country, state):
        """Returns the districts for the country and state given

        :param country: name or iso of the country
        :param state: name or code of the state
        :return: a list of districts
        """
        iso = self.get_country_iso(country)
        state_code = self.get_state_code(iso, state)
        districts = filter(lambda dis: dis[0] == iso, DISTRICTS)
        districts = filter(lambda dis: dis[1] == state_code, districts)
        return map(lambda dis: dis[2], districts)

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
