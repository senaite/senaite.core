# -*- coding: utf-8 -*-

from datetime import datetime

from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import IDatetimeField
from zope.interface import implementer
from zope.schema import Datetime


@implementer(IDatetimeField)
class DatetimeField(Datetime, BaseField):
    """A field that handles date and time
    """

    def set(self, object, value):
        """Set UID reference

        :param object: the instance of the field
        :param value: datetime value
        :type value: datetime
        """
        super(DatetimeField, self).set(object, value)

    def _validate(self, value):
        """Validator when called from form submission
        """
        super(DatetimeField, self)._validate(value)
