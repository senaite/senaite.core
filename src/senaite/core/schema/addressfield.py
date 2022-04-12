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

import copy
import six

from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import IAddressField
from zope.interface import implementer
from zope.schema import List
from zope.schema.interfaces import IFromUnicode

NAIVE_ADDRESS = "naive"
PHYSICAL_ADDRESS = "physical"
POSTAL_ADDRESS = "postal"
BILLING_ADDRESS = "billing"
BUSINESS_ADDRESS = "business"
OTHER_ADDRESS = "other"


@implementer(IAddressField, IFromUnicode)
class AddressField(List, BaseField):
    """A field that handles a single or multiple physical addresses
    """

    def __init__(self, address_types=None, **kw):
        if address_types is None:
            # Single address
            address_types = (NAIVE_ADDRESS,)
        self.address_types = address_types
        super(AddressField, self).__init__(**kw)

    def get_address_types(self):
        """Returns a tuple with the types of address handled by this field
        (e.g. address, postal-address, etc.)
        """
        address_types = self.address_types
        if not address_types:
            address_types = ()
        elif isinstance(address_types, six.string_types):
            address_types = (address_types, )
        return address_types

    def is_multi_address(self):
        """Returns whether this field handles multiple addresses
        """
        return len(self.get_address_types()) > 1

    def to_list(self, value, filter_empty=True):
        """Ensure the value is a list
        """
        if not isinstance(value, list):
            value = [value]
        if filter_empty:
            value = filter(None, value)
        return value

    def set(self, object, value):
        """Set an address record or records
        :param object: the instance of the field
        :param value: dict with address information or list of dicts
        :type value: list/tuple/dict
        """
        # Value is a list of dicts
        value = self.to_list(value)

        # Bail out non-supported address types
        address_types = self.get_address_types()
        value = filter(lambda ad: ad["type"] in address_types, value)

        # Set the value
        super(AddressField, self).set(object, value)

    def get(self, object):
        """Returns the address records
        :param object: the instance of this field
        :returns: list of dicts with address information for each address type
        """
        addresses = super(AddressField, self).get(object) or []

        # Sort and extend with non-existing address types
        output = []
        for address_type in self.get_address_types():
            address = filter(lambda rec: rec["type"] == address_type, addresses)
            if address:
                address = copy.deepcopy(address[0])
            else:
                address = self.get_empty_address(address_type)
            output.append(address)

        # Sort address in same order as types
        return output

    def get_empty_address(self, address_type):
        """Returns a dict that represents an empty address for the given type
        """
        return {
            "type": address_type,
            "address": "",
            "zip": "",
            "city": "",
            "subdivision2": "",
            "subdivision1": "",
            "country": "",
        }

    def _validate(self, value):
        """Validator called on form submit
        """
        super(AddressField, self)._validate(value)
