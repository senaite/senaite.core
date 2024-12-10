# -*- coding: utf-8 -*-

from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import ISelectOtherField
from zope.interface import implementer
from zope.schema import Choice


@implementer(ISelectOtherField)
class SelectOtherField(Choice, BaseField):
    """A field that handles a value from a predefined vocabulary or custom
    """
    def _validate(self, value):
        super(SelectOtherField, self)._validate(value)
