# -*- coding: utf-8 -*-

from datetime import datetime

import pytz
from bika.lims import api
from plone.app.z3cform.converters import DatetimeWidgetConverter
from Products.CMFPlone.utils import safe_callable
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IDatetimeField
from senaite.core.z3cform.interfaces import IDatetimeWidget
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import implementer

DATE_ONLY = ("{value.year:}-{value.month:02}-{value.day:02}")

DATE_AND_TIME = ("{value.year:}-{value.month:02}-{value.day:02} "
                 "{value.hour:02}:{value.minute:02}")


@adapter(IDatetimeField, interfaces.IWidget)
class DatetimeDataConverter(DatetimeWidgetConverter):
    """Converts the raw field data for widget/field usage
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
        return super(DatetimeDataConverter, self).toFieldValue(value)


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

        NOTE: IMO opinion the timezone won't be ever set unless the widget
              `default_timezone` is set explicitly.

        code taken from here:
        `plone.app.z3cform.converters.DatetimeWidgetConverter`

        :param value: date or datetime
        :type value: string or datetime object
        :returns: datetime object
        """
        if isinstance(value, datetime):
            return value
        if not value:
            return ""
        tmp = value.split(" ")
        if not tmp[0]:
            return ""
        value = tmp[0].split("-")
        if len(tmp) == 2 and ":" in tmp[1]:
            value += tmp[1].split(":")
        else:
            value += ["00", "00"]

        default_zone = self.default_timezone
        zone = default_zone(self.context) \
            if safe_callable(default_zone) else default_zone
        ret = datetime(*map(int, value))
        if zone:
            tzinfo = pytz.timezone(zone)
            ret = tzinfo.localize(ret)
        return ret

    def get_date(self, value):
        """Return only the date part of the value

        :returns: date string
        """
        dt = self.to_datetime(value)
        if not dt:
            return ""
        return dt.strftime("%Y-%m-%d")

    def get_time(self, value):
        """Return only the time part of the value

        :returns: time string
        """
        dt = self.to_datetime(value)
        if not dt:
            return ""
        return dt.strftime("%H:%M")

    def get_max(self):
        """Return the max allowed date in the future

        :returns: date string
        """
        now = datetime.now()
        return now.strftime("%Y-%m-%d")

    def get_min(self):
        """Return the min allowed date in the past

        :returns: date string
        """
        now = datetime.now()
        return now.strftime("%Y-%m-%d")

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
