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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from datetime import date
from datetime import datetime

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from dateutil import relativedelta
from Products.Archetypes.interfaces import IDateTimeField
from Products.Archetypes.public import *
from Products.Archetypes.public import DateTimeField as DTF
from Products.Archetypes.Registry import registerField
from zope.i18n import translate
from zope.i18nmessageid import Message
from zope.interface import implements

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import get_date
from bika.lims.browser import ulocalized_time

WIDGET_NOPAST = "datepicker_nopast"
WIDGET_2MONTHS = "datepicker_2months"
WIDGET_NOFUTURE = "datepicker_nofuture"
WIDGET_SHOWTIME = "show_time"


class DateTimeField(DTF):
    """A field that stores dates and times
    This is identical to the AT widget on which it's based, but it checks
    the i18n translation values for date formats.  This does not specifically
    check the date_format_short_datepicker, so this means that date_formats
    should be identical between the python strftime and the jquery version.
    """

    _properties = Field._properties.copy()
    _properties.update({
        'type': 'datetime',
        'widget': CalendarWidget,
    })

    implements(IDateTimeField)

    security = ClassSecurityInfo()

    security.declarePrivate('set')

    def set(self, instance, value, **kwargs):
        """
        Check if value is an actual date/time value. If not, attempt
        to convert it to one; otherwise, set to None. Assign all
        properties passed as kwargs to object.
        """
        val = get_date(instance, value)
        super(DateTimeField, self).set(instance, val, **kwargs)

    def validate(self, value, instance, errors=None, **kwargs):
        """Validate passed-in value using all field validators plus the
        validators for minimum and maximum date values
        Return None if all validations pass; otherwise, return the message of
        of the validation failure translated to current language
        """
        # Rely on the super-class first
        error = super(DateTimeField, self).validate(
            value, instance, errors=errors, **kwargs)
        if error:
            return error

        # Return immediately if we have no value and the field is not required
        if not value and not self.required:
            return

        # Validate value is after min date
        error = self.validate_min_date(value, instance, errors=errors)
        if error:
            return error

        # Validate value is before max date
        error = self.validate_max_date(value, instance, errors=errors)
        if error:
            return error

    def to_ansi(self, dt, show_time=True):
        """Returns the date in ANSI X3.30/X4.43.3) format
        :param dt: DateTime/datetime/date
        :param show_time: if true, returns YYYYMMDDHHMMSS. YYYYMMDD otherwise
        :returns: str that represents the datetime in ANSI format
        """
        if isinstance(dt, DateTime):
            dt = dt.asdatetime()
        elif not isinstance(dt, (date, datetime)):
            return None

        ansi = "{:04d}{:02d}{:02d}".format(dt.year, dt.month, dt.day)
        if not show_time:
            return ansi
        return "{}{:02d}{:02d}{:02d}".format(ansi, dt.hour, dt.minute, dt.second)

    def validate_min_date(self, value, instance, errors=None):
        """Validates the passed-in value against the field's minimum date
        """
        if errors is None:
            errors = {}

        # self.min always returns an offset-naive datetime, but the value
        # is offset-aware. We need to add the TZ, otherwise we get a:
        #   TypeError: can't compare offset-naive and offset-aware datetimes
        value = get_date(instance, value)
        if self.to_ansi(value) >= self.to_ansi(self.min):
            return None

        error = _(
            u"error_datetime_before_min",
            default=u"${name} is before ${min_date}, please correct.",
            mapping={
                "name": self.get_label(instance),
                "min_date": self.localize(self.min, instance) or repr(self.min)
            }
        )

        field_name = self.getName()
        errors[field_name] = translate(error, context=api.get_request())
        return errors[field_name]

    def validate_max_date(self, value, instance, errors=None):
        """Validates the passed-in value against the field's maximum date
        """
        if errors is None:
            errors = {}

        # self.max always returns an offset-naive datetime, but the value
        # is offset-aware. We need to add the TZ, otherwise we get a:
        #   TypeError: can't compare offset-naive and offset-aware datetimes
        value = get_date(instance, value)
        if self.to_ansi(value) <= self.to_ansi(self.max):
            return None

        error = _(
            u"error_datetime_after_max",
            default=u"${name} is after ${max_date}, please correct.",
            mapping={
                "name": self.get_label(instance),
                "max_date": self.localize(self.max, instance) or repr(self.max)
            }
        )

        field_name = self.getName()
        errors[field_name] = translate(error, context=api.get_request())
        return errors[field_name]

    def is_true(self, val):
        """Returns whether val evaluates to True
        """
        val = str(val).strip().lower()
        return val in ["y", "yes", "1", "true", "on"]

    def get_label(self, instance):
        """Returns the translated label of this field for the given instance
        """
        request = api.get_request()
        label = self.widget.Label(instance)
        if isinstance(label, Message):
            return translate(label, context=request)
        return label

    def localize(self, dt, instance):
        """Returns the dt to localized time
        """
        request = api.get_request()
        return ulocalized_time(dt, long_format=self.show_time,
                               context=instance, request=request)

    @property
    def min(self):
        """Returns the minimum datetime supported by this field
        """
        no_past = getattr(self.widget, WIDGET_NOPAST, False)
        if self.is_true(no_past):
            return datetime.now()
        return datetime.min

    @property
    def max(self):
        """Returns the maximum datetime supported for this field
        """
        no_future = getattr(self.widget, WIDGET_NOFUTURE, False)
        if self.is_true(no_future):
            return datetime.now()
        two_months = getattr(self.widget, WIDGET_2MONTHS, False)
        if self.is_true(two_months):
            return datetime.now() + relativedelta(months=2)
        return datetime.max

    @property
    def show_time(self):
        """Returns whether the time is displayed by the widget
        """
        show_time = getattr(self.widget, WIDGET_SHOWTIME, False)
        return self.is_true(show_time)


registerField(DateTimeField,
              title='Date Time',
              description='Used for storing date/time')
