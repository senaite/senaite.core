# -*- coding: utf-8 -*-

from senaite.core.api import dtime
from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import IDatetimeField
from zope.interface import implementer
from zope.schema import Datetime


def localize(dt, fallback="UTC"):
    if dtime.is_timezone_naive(dt):
        zone = dtime.get_os_timezone()
        if not zone:
            zone = fallback
        dt = dtime.to_zone(dt, zone)
    return dt


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
        if dtime.is_dt(value):
            value = localize(value)
        super(DatetimeField, self).set(object, value)

    def get(self, object):
        """Get the current date

        :param object: the instance of the field
        :returns: datetime or None
        """
        value = super(DatetimeField, self).get(object)
        if not dtime.is_dt(value):
            return None
        return localize(value)

    def _validate(self, value):
        """Validator when called from form submission
        """
        super(DatetimeField, self)._validate(value)
