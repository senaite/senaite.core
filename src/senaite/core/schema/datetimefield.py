# -*- coding: utf-8 -*-

from datetime import datetime

import pytz
from plone.app.event.base import default_timezone as current_timezone
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

    def get(self, object):
        """Get the current date

        :param object: the instance of the field
        :returns: datetime or None
        """
        value = super(DatetimeField, self).get(object)
        if not isinstance(value, datetime):
            return None
        # append current timezone if timezone naive
        if value.tzinfo is None:
            tz = current_timezone()
            tzinfo = pytz.timezone(tz)
            value = tzinfo.localize(value)
        return value

    def _validate(self, value):
        """Validator when called from form submission
        """
        super(DatetimeField, self)._validate(value)
