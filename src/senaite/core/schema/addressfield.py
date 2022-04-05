# -*- coding: utf-8 -*-

import six

from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import IAddressField
from zope.interface import implementer
from zope.schema import List

NAIVE_ADDRESS = "Address"
PHYSICAL_ADDRESS = "Physical Address"
POSTAL_ADDRESS = "Postal Address"
BILLING_ADDRESS = "Billing Address"
BUSINESS_ADDRESS = "Business Address"
OTHER_ADDRESS = "Other Address"


@implementer(IAddressField)
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
        return super(AddressField, self).get(object) or []

    def _validate(self, value):
        """Validator called on form submit
        """
        super(AddressField, self)._validate(value)
