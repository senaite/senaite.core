# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from time import strptime

from AccessControl import ClassSecurityInfo

from DateTime.DateTime import DateTime, safelocaltime
from DateTime.interfaces import DateTimeError
from Products.Archetypes.Registry import registerField
from Products.Archetypes.interfaces import IDateTimeField
from Products.Archetypes.public import *
from Products.Archetypes.public import DateTimeField as DTF
from Products.ATContentTypes.utils import dt2DT
from bika.lims import logger
from zope.interface import implements
import datetime


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


    def get_datetime_from_locale_format(self, instance, date_string):
        """Converts a date string to a datetime object
        """
        default_format = "%Y-%m-%d"
        locale_key = "date_format_short"
        if self.widget.show_time:
            locale_key = "date_format_long"
            default_format += " %H:%M"

        locale_format = instance.translate(locale_key, domain="senaite.core",
                                           mapping={})
        if locale_format != locale_key:
            # Custom format set. Try to convert
            # e.g: locale format is "%b %d, %Y %I:$M %p" and the date_string
            # passed in is "Sep 12, 2018 12:46 PM"
            try:
                struct_time = strptime(date_string, locale_format)
                return datetime.datetime(*struct_time[:6])
            except ValueError:
                logger.warn("Unable to convert to DateTime {} using format {}".
                            format(date_string, locale_format))

        # Try with default format used by DateTimeWidget
        struct_time = strptime(date_string, default_format)
        return datetime.datetime(*struct_time[:6])


    def set(self, instance, value, **kwargs):
        """
        Check if value is an actual date/time value. If not, attempt
        to convert it to one; otherwise, set to None. Assign all
        properties passed as kwargs to object.
        """
        val = value
        if not value:
            val = None

        if isinstance(value, basestring):
            # Try to translate to clo
            val = self.get_datetime_from_locale_format(instance, value)
            val = dt2DT(val)
            if val.timezoneNaive():
                # Use local timezone for tz naive strings
                # see http://dev.plone.org/plone/ticket/10141
                zone = val.localZone(safelocaltime(val.timeTime()))
                parts = val.parts()[:-1] + (zone,)
                val = DateTime(*parts)

        elif isinstance(value, datetime.datetime):
            val = dt2DT(value)

        super(DateTimeField, self).set(instance, val, **kwargs)

registerField(DateTimeField,
              title='Date Time',
              description='Used for storing date/time')
