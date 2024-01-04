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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from datetime import datetime

from bika.lims import api
from senaite.core.api import dtime
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IDatetimeField
from senaite.core.z3cform.interfaces import IDatetimeWidget
from senaite.core.z3cform.widgets.basewidget import BaseWidget
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IDataManager
from z3c.form.interfaces import IFieldWidget
from z3c.form.validator import SimpleFieldValidator
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

HOUR_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

DATE_ONLY = ("{value.year:}-{value.month:02}-{value.day:02}")

DATE_AND_TIME = ("{value.year:}-{value.month:02}-{value.day:02} "
                 "{value.hour:02}:{value.minute:02}")


@adapter(
    Interface,           # context
    ISenaiteFormLayer,   # request
    interfaces.IForm,    # form
    IDatetimeField,      # field
    interfaces.IWidget,  # widget
)
class DatetimeDataValidator(SimpleFieldValidator):
    """Datetime validator

    Adapter looked up by `z3c.form.field.extract()` when storing a new value
    """
    def validate(self, value, force=True):
        # we always force to avoid comparison of datetime objects, which might
        # eventually raise this error `TypeError`:
        #
        # TypeError: can't compare offset-naive and offset-aware datetimes
        return super(DatetimeDataValidator, self).validate(value, force=True)


@adapter(IDatetimeField, interfaces.IWidget)
class DatetimeDataConverter(BaseDataConverter):
    """Converts the value between the field and the widget
    """
    def toWidgetValue(self, value):
        """Converts from field value to widget.

        This value will be set to the hidden field and does not reflect the
        date that is visible to the user!

        called by `z3c.form.widget.update`

        Bases:
            `plone.app.z3cform.converters.DatetimeWidgetConverter`
            `z3c.form.converter.DatetimeDataConverter`

        :param value: Field value.
        :type value: datetime

        :returns: Datetime in format `Y-m-d H:M`
        :rtype: string
        """
        if value is None:
            return u""
        if getattr(self.widget, "show_time", None) is False:
            return DATE_ONLY.format(value=value)
        return DATE_AND_TIME.format(value=value)

    def toFieldValue(self, value):
        """Converts from widget (date string) value to field value (datetime)

        :param value: Date string inserted by datetime widget.
        :type value: string

        :returns: `datetime.datetime` object.
        :rtype: datetime
        """
        default = getattr(self.field, "missing_value", None)
        timezone = self.widget.default_timezone or dtime.get_os_timezone()
        return to_datetime(value, timezone=timezone, default=default)


def to_datetime(value, timezone=None, default=None):
    """Convert the value to a datetime object

    Code originally taken from here:
    `plone.app.z3cform.converters.DatetimeWidgetConverter.toFieldValue`

    :param value: Value inserted by datetime widget.
    :type value: string
    """
    if isinstance(value, datetime):
        return value
    if not value:
        return default
    tmp = value.split(" ")
    if not tmp[0]:
        return default
    value = tmp[0].split("-")
    if len(tmp) == 2 and ":" in tmp[1]:
        value += tmp[1].split(":")
    else:
        value += ["00", "00"]

    ret = datetime(*map(int, value))
    if timezone:
        if callable(timezone):
            timezone = timezone()
        ret = dtime.to_zone(ret, timezone)
    return ret


@implementer(IDatetimeWidget)
class DatetimeWidget(HTMLInputWidget, BaseWidget):
    """Senaite date and time widget
    """
    klass = u"senaite-datetime-widget"
    # Olson DB/pytz timezone identifier or a callback
    # returning such an identifier.
    default_timezone = None
    # enable/disable time component
    show_time = True

    def __init__(self, request, *args, **kw):
        super(DatetimeWidget, self).__init__(request)
        self.request = request
        self._min = None
        self._max = None

    def update(self):
        """Computes self.value for the widget templates

        see z3c.form.widget.Widget
        """
        super(DatetimeWidget, self).update()
        widget.addFieldClass(self)

    def to_localized_time(self, time, long_format=None, time_only=None):
        """Convert time to localized time
        """
        dt = self.to_datetime(time)
        long_format = True if self.show_time else False
        return dtime.to_localized_time(dt, long_format, time_only)

    def get_display_value(self):
        """Returns the localized date value
        """
        value = self.value
        dm = queryMultiAdapter((self.context, self.field), IDataManager)
        if dm:
            # extract the object from the database
            value = dm.query()
        if not dtime.is_date(value):
            return None
        return self.to_localized_time(value)

    def to_datetime(self, value):
        """convert date string to datetime object with tz

        :param value: date or datetime
        :type value: string or datetime object
        :returns: datetime object
        """
        default = getattr(self.field, "missing_value", None)
        timezone = self.default_timezone
        return to_datetime(value, timezone=timezone, default=default)

    def get_date(self, value):
        """Return only the date part of the value

        :returns: date string
        """
        dt = self.to_datetime(value)
        if not dt:
            return u""
        return dtime.date_to_string(dt, DATE_FORMAT)

    def get_time(self, value):
        """Return only the time part of the value

        :returns: time string
        """
        dt = self.to_datetime(value)
        if not dt:
            return u""
        return dtime.date_to_string(dt, HOUR_FORMAT)

    def attrs(self):
        """Return the template attributes for the date field

        :returns: dictionary of HTML attributes
        """
        return {
            "min": dtime.date_to_string(self.min),
            "max": dtime.date_to_string(self.max),
        }

    @property
    def min(self):
        """Returns the minimum date allowed for selection in the widget
        """
        if self._min is None:
            func = getattr(self.field, "get_min", None)
            context = self.get_context()
            self._min = func(context) if func else datetime.min
        return self._min

    @min.setter
    def min(self, value):
        self._min = value

    @property
    def max(self):
        """Returns the maximum date allowed for selection in the widget
        """
        if self._max is None:
            func = getattr(self.field, "get_max", None)
            context = self.get_context()
            self._max = func(context) if func else datetime.max
        return self._max

    @max.setter
    def max(self, value):
        self._max = value

    @property
    def portal(self):
        """Return the portal object
        """
        return api.get_portal()

    @property
    def portal_url(self):
        """Return the portal object URL
        """
        return api.get_url(self.portal)


@adapter(IDatetimeField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def DatetimeWidgetFactory(field, request):
    """Widget factory for datetime field
    """
    return FieldWidget(field, DatetimeWidget(request))
