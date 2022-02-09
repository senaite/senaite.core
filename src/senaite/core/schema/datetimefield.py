# -*- coding: utf-8 -*-

from senaite.core.api import dtime
from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import IDatetimeField
from zope.interface import implementer
from zope.schema import Datetime


@implementer(IDatetimeField)
class DatetimeField(Datetime, BaseField):
    """A field that handles date and time
    """

    def set(self, object, value):
        """Set datetime value

        NOTE: we need to ensure timzone aware datetime values,
              so that also API calls work

        :param object: the instance of the field
        :param value: datetime value
        :type value: datetime
        """
        value = dtime.to_dt(value)
        super(DatetimeField, self).set(object, value)

    def get(self, object):
        """Get the current date

        :param object: the instance of the field
        :returns: datetime or None
        """
        value = super(DatetimeField, self).get(object)
        # ensure we have a `datetime` object
        dt = dtime.to_dt(value)
        # ensure we have always a date with a valid timezone
        if dt and dtime.is_timezone_naive(dt):
            # append default OS timezone
            tz = dtime.get_os_timezone()
            dt = dtime.to_zone(dt, tz)
        return dt

    def _validate(self, value):
        """Validator when called from form submission
        """
        super(DatetimeField, self)._validate(value)
