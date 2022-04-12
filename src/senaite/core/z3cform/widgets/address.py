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
import six
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from senaite.core.api import geo
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IAddressField
from senaite.core.z3cform.interfaces import IAddressWidget
from z3c.form.browser.widget import HTMLFormElement
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IWidget
from z3c.form.interfaces import NO_VALUE
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import implementer


@adapter(IAddressField, IWidget)
class AddressDataConverter(BaseDataConverter):
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
        values = self.to_list_of_dicts(value)
        return self.to_utf8(values)

    def toFieldValue(self, value):
        """Converts from widget value to safe_unicode
        """
        values = self.to_list_of_dicts(value)
        return self.to_safe_unicode(values)

    def to_safe_unicode(self, data):
        """Converts the data to unicode
        """
        if isinstance(data, unicode):
            return data
        if isinstance(data, list):
            return [self.to_safe_unicode(item) for item in data]
        if isinstance(data, dict):
            return {
                self.to_safe_unicode(key): self.to_safe_unicode(value)
                for key, value in six.iteritems(data)
            }
        return safe_unicode(data)

    def to_utf8(self, data):
        """Encodes the data to utf-8
        """
        if isinstance(data, unicode):
            return data.encode("utf-8")
        if isinstance(data, list):
            return [self.to_utf8(item) for item in data]
        if isinstance(data, dict):
            return {
                self.to_utf8(key): self.to_utf8(value)
                for key, value in six.iteritems(data)
            }
        return data


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
            "{subdivision2}, {subdivision1}",
            "{country}"
        ]

        # Skip the type if multi-address
        if not self.field.is_multi_address():
            lines = lines[1:]

        return "<br/>".join(lines)

    def get_formatted_address(self, address):
        """Returns the address formatted in html
        """
        address_format = self.get_address_format()
        lines = address_format.split("<br/>")
        values = map(lambda line: line.format(**address), lines)
        # Some extra cleanup
        values = map(lambda line: line.strip(",- "), values)
        values = filter(lambda line: line != "()", values)
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

    def extract(self, default=NO_VALUE):
        """Extracts the value based on the request and nothing else
        """
        mapping = {}
        prefix = "{}.".format(self.name)
        keys = filter(lambda key: key.startswith(prefix), self.request.keys())
        for key in keys:
            val = key.replace(prefix, "")
            idx, subfield_name = val.split(".")
            if not api.is_floatable(idx):
                continue

            empty_record = self.field.get_empty_address("")
            mapping.setdefault(api.to_int(idx), empty_record).update({
                subfield_name: self.request.get(key)
            })

        # Return the list of items sorted correctly
        records = []
        for index in sorted(mapping.keys()):
            record = mapping.get(index)
            records.append(record)

        return records or default

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
            "data-labels": {
                "country": api.to_utf8(_("Country")),
                "subdivision1": api.to_utf8(_("State")),
                "subdivision2": api.to_utf8(_("District")),
                "city": api.to_utf8(_("City")),
                "zip": api.to_utf8(_("Postal code")),
                "address": api.to_utf8(_("Address")),
            },
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


class AjaxSubdivisions(BrowserView):
    """Endpoint for the retrieval of geographic subdivisions
    """

    def __call__(self):
        """Returns a json with the list of geographic subdivisions that are
        immediately below the country or subdivision passed in with `parent`
        parameter via POST/GET
        """
        items = []
        parent = self.get_parent()
        if not parent:
            return json.dumps(items)

        # Extract the subdivisions for this parent
        parent = safe_unicode(parent)
        items = geo.get_subdivisions(parent, default=[])
        items = map(lambda sub: [sub.country_code, sub.code, sub.name], items)
        return json.dumps(items)

    def get_parent(self):
        """Returns the parent passed through the request
        """
        parent = self.request.get("parent", None)
        if not parent:
            values = json.loads(self.request.get("BODY", "{}"))
            parent = values.get("parent", None)
        return parent
