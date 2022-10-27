# -*- coding: utf-8 -*-

from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import IPhoneField
from zope.interface import implementer
from zope.schema import NativeString


@implementer(IPhoneField)
class PhoneField(NativeString, BaseField):
    """A field that handles phone numbers
    """
    def _validate(self, value):
        super(PhoneField, self)._validate(value)
