# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from time import strptime

from AccessControl import ClassSecurityInfo

from DateTime.DateTime import DateTime, safelocaltime
from DateTime.interfaces import DateTimeError
from Products.Archetypes.Registry import registerField
from Products.Archetypes.interfaces import IDateTimeField
from Products.Archetypes.public import *
from Products.Archetypes.public import DateTimeField as DTF
from bika.lims.browser import strptime
from zope.interface import implements


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
        val = value
        if not value:
            val = None
        elif not isinstance(value, DateTime):
            val = strptime(instance, value)

        super(DateTimeField, self).set(instance, val, **kwargs)

registerField(DateTimeField,
              title='Date Time',
              description='Used for storing date/time')
