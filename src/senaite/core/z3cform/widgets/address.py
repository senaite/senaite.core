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
from bika.lims.decorators import returns_json
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from senaite.core.api import geo
from senaite.core.decorators import readonly_transaction
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.addressfield import BILLING_ADDRESS
from senaite.core.schema.addressfield import BUSINESS_ADDRESS
from senaite.core.schema.addressfield import NAIVE_ADDRESS
from senaite.core.schema.addressfield import OTHER_ADDRESS
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.schema.addressfield import POSTAL_ADDRESS
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

    # Address html format for display. Wildcards accepted: {type},
    # {address_type}, {zip}, {city}, {district}, {subdivision1}, {subdivision2},
    # {country}. Use '<br/>' for newlines
    address_format = ""

    # Mapping between address_types and their names for i18n
    address_types = {
        NAIVE_ADDRESS: _("Address"),
        PHYSICAL_ADDRESS: _("Physical address"),
        POSTAL_ADDRESS: _("Postal address"),
        BILLING_ADDRESS: _("Billing address"),
        BUSINESS_ADDRESS: _("Business address"),
        OTHER_ADDRESS: _("Other address"),
    }

    def get_address_format(self):
        """Returns the format for displaying the address
        """
        if self.address_format:
            return self.address_format

        lines = [
            "<strong>{address_type}</strong>",
            "{address}",
            "{zip} {city}",
            "{subdivision2}, {subdivision1}",
            "{country}"
        ]

        # Skip the type if multi-address
        if not self.field.is_multi_address():
            lines = lines[1:]

        return "<br/>".join(lines)

    def get_formatted_address(self, data):
        """Returns the address formatted in html
        """
        address = {
            "address_type": "",
            "address": "",
            "zip": "",
            "city": "",
            "country": "",
            "subdivision1": "",
            "subdivision2": "",
        }
        address.update(data)

        address_format = self.get_address_format()

        # Inject the name of the type of address translated
        address_type = address.get("type")
        address_type_name = self.address_types.get(address_type, address_type)
        address.update({
            "address_type": address.get("address_type", address_type_name)
        })

        lines = address_format.split("<br/>")
        values = map(lambda line: line.format(**address), lines)
        # Some extra cleanup
        values = map(lambda line: line.strip(",- "), values)
        values = filter(lambda line: line != "()", values)
        values = filter(None, values)
        return "<br/>".join(values)

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

    def get_value(self):
        values = self.value or []
        existing = dict([(a.get("type"), a) for a in values])

        # HACK - This is necessary for when adding a new object, cause current
        # context is the container instead of an object with the desired type
        output = []
        for address_type in self.field.get_address_types():
            default = self.field.get_empty_address(address_type)
            output.append(existing.get(address_type, default))
        return output

    def get_input_widget_attributes(self):
        """Return input widget attributes for the ReactJS component
        """
        translate = self.context.translate
        countries = map(lambda c: c.name, geo.get_countries())
        labels = {country: {} for country in countries}
        labels.update({
            "country": translate(_("Country")),
            "subdivision1": translate(_("State")),
            "subdivision2": translate(_("District")),
            "city": translate(_("City")),
            "zip": translate(_("Postal code")),
            "address": translate(_("Address"))
        })
        sub1 = {}
        sub2 = {}

        for item in self.get_value():
            country = item.get("country")
            if country and country not in sub1:
                subdivisions = geo.get_subdivisions(country, [])
                sub1[country] = map(lambda sub: sub.name, subdivisions)

                label = _("State")
                if subdivisions:
                    label = _(subdivisions[0].type)
                labels[country]["subdivision1"] = translate(label)

            subdivision1 = item.get("subdivision1")
            if subdivision1 and subdivision1 not in sub2:
                subdivisions = geo.get_subdivisions(subdivision1, [])
                sub2[subdivision1] = map(lambda sub: sub.name, subdivisions)

                label = _("District")
                if subdivisions:
                    label = _(subdivisions[0].type)
                labels[country]["subdivision2"] = translate(label)

        attributes = {
            "data-id": self.id,
            "data-countries": countries,
            "data-subdivisions1": sub1,
            "data-subdivisions2": sub2,
            "data-name": self.name,
            "data-portal_url": api.get_url(api.get_portal()),
            "data-items": self.get_value(),
            "data-title": self.title,
            "data-class": self.klass,
            "data-style": self.style,
            "data-disabled": self.disabled or False,
            "data-labels": labels
        }

        # Generate the i18n labels for address types
        for a_type, name in self.address_types.items():
            attributes["data-labels"].update({
                a_type: translate(name)
            })

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

    @readonly_transaction
    @returns_json
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

        def to_dict(subdivision):
            return {
                "name": subdivision.name,
                "code": subdivision.code,
                "type": self.context.translate(_(subdivision.type)),
            }
        return [to_dict(item) for item in items]

    def get_parent(self):
        """Returns the parent passed through the request
        """
        parent = self.request.get("parent", None)
        if not parent:
            values = json.loads(self.request.get("BODY", "{}"))
            parent = values.get("parent", None)
        return parent
