# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta

import pytz
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from plone.app.event.base import default_timezone as current_timezone
from Products.CMFPlone.utils import safe_callable
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IDatetimeField
from senaite.core.z3cform.interfaces import IDatetimeWidget
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.validator import SimpleFieldValidator
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer

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
    def validate(self, value, force=False):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return _("No timezone found for date %r" % value)
        return super(DatetimeDataValidator, self).validate(value, force)


@adapter(IDatetimeField, interfaces.IWidget)
class DatetimeDataConverter(BaseDataConverter):
    """Converts the value between the field and the widget
    """
    def toWidgetValue(self, value):
        """Converts from field value to widget.

        called by `z3c.form.widget.update`

        Bases:
            `plone.app.z3cform.converters.DatetimeWidgetConverter`
            `z3c.form.converter.DatetimeDataConverter`

        :param value: Field value.
        :type value: datetime

        :returns: Datetime in format `Y-m-d H:M`
        :rtype: string
        """
        if value is self.field.missing_value:
            return u""
        if getattr(self.widget, "show_time", None) is False:
            return DATE_ONLY.format(value=value)
        return DATE_AND_TIME.format(value=value)

    def toFieldValue(self, value):
        """Converts from widget value to field.

        :param value: Value inserted by datetime widget.
        :type value: string

        :returns: `datetime.datetime` object.
        :rtype: datetime
        """
        default = self.field.missing_value
        timezone = self.widget.get_timezone()
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
        tzinfo = pytz.timezone(timezone)
        ret = tzinfo.localize(ret)
    return ret


@implementer(IDatetimeWidget)
class DatetimeWidget(HTMLInputWidget, Widget):
    """Senaite date and time widget
    """
    klass = u"senaite-datetime-widget"
    # Olson DB/pytz timezone identifier or a callback
    # returning such an identifier.
    default_timezone = None
    # enable/disable time component
    show_time = True
    # disable past dates in the date picker
    datepicker_nopast = False
    # disable future dates in the date picker
    datepicker_nofuture = False

    def __init__(self, request, *args, **kw):
        super(DatetimeWidget, self).__init__(request)
        self.request = request

    def update(self):
        """Computes self.value for the widget templates

        see z3c.form.widget.Widget
        """
        super(DatetimeWidget, self).update()
        widget.addFieldClass(self)

    def get_timezone(self):
        """Return the current timezone
        """
        default_zone = self.default_timezone
        timezone = default_zone(self.context)\
            if safe_callable(default_zone) else default_zone
        if not timezone:
            # return computed timezone
            timezone = current_timezone(context=self.context, as_tzinfo=False)
        return timezone

    def to_localized_time(self, time, long_format=None, time_only=None):
        """Convert time to localized time
        """
        ts = api.get_tool("translation_service")
        long_format = True if self.show_time else False
        return ts.ulocalized_time(
            time, long_format, time_only, self.context, domain="senaite.core")

    def to_local_date(self, value, length="short"):
        """Converts value to localized date

        Used in the display template to show a localized version of the date

        :param value: date or datetime
        :type value: string or datetime object
        :returns: localized date string
        """
        dt = self.to_datetime(value)
        if not dt:
            return ""
        df = "dateTime" if self.show_time else "date"
        formatter = self.request.locale.dates.getFormatter(df, length)
        return formatter.format(dt)

    def to_datetime(self, value):
        """convert date string to datetime object with tz

        :param value: date or datetime
        :type value: string or datetime object
        :returns: datetime object
        """
        default = self.field.missing_value
        timezone = self.get_timezone()
        return to_datetime(value, timezone=timezone, default=default)

    def get_date(self, value):
        """Return only the date part of the value

        :returns: date string
        """
        dt = self.to_datetime(value)
        if not dt:
            return u""
        return dt.strftime(DATE_FORMAT)

    def get_time(self, value):
        """Return only the time part of the value

        :returns: time string
        """
        dt = self.to_datetime(value)
        if not dt:
            return u""
        return dt.strftime(HOUR_FORMAT)

    def date_now(self, offset=0):
        """Get the current date without time component
        """
        ts = datetime.now().strftime(DATE_FORMAT)
        dt = datetime.strptime(ts, DATE_FORMAT)
        if offset:
            dt = dt + timedelta(offset)
        return dt

    def get_max(self):
        """Return the max allowed date in the future

        :returns: date string
        """
        now = self.date_now()
        return now.strftime(DATE_FORMAT)

    def get_min(self):
        """Return the min allowed date in the past

        :returns: date string
        """
        now = self.date_now()
        return now.strftime(DATE_FORMAT)

    def attrs(self):
        """Return the template attributes for the date field

        :returns: dictionary of HTML attributes
        """
        attrs = {}
        if self.datepicker_nofuture:
            attrs["max"] = self.get_max()
        if self.datepicker_nopast:
            attrs["min"] = self.get_min()
        return attrs

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
