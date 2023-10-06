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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims.browser import ulocalized_time as ut
from DateTime import DateTime
from DateTime.DateTime import safelocaltime
from DateTime.interfaces import DateTimeError
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from senaite.core.api import dtime


class DateTimeWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        "show_time": False,
        "min": dtime.datetime.min,
        "max": dtime.datetime.max,
        "macro": "senaite_widgets/datetimewidget",
        "helper_js": ("senaite_widgets/datetimewidget.js",),
        "helper_css": ("senaite_widgets/datetimewidget.css",),
    })

    security = ClassSecurityInfo()

    def ulocalized_time(self, time, context, request):
        """Returns the localized time in string format
        """
        value = ut(time, long_format=self.show_time, time_only=False,
                   context=context, request=request)
        return value or ""

    def to_tz_date(self, value):
        if not isinstance(value, DateTime):
            try:
                value = DateTime(value)
                if value.timezoneNaive():
                    # Use local timezone for tz naive strings
                    # see http://dev.plone.org/plone/ticket/10141
                    zone = value.localZone(safelocaltime(value.timeTime()))
                    parts = value.parts()[:-1] + (zone,)
                    value = DateTime(*parts)
            except DateTimeError:
                value = None
        return value

    def to_local_date(self, time, context, request):
        """This method converts to a local date w/o timezone
        """
        dt = self.to_tz_date(time)
        if self.show_time:
            return dtime.date_to_string(dt, "%Y-%m-%dT%H:%M")
        return dtime.date_to_string(dt, "%Y-%m-%d")

    def get_date(self, value):
        if not value:
            return ""
        dt = self.to_tz_date(value)

        return dtime.date_to_string(dt, "%Y-%m-%d")

    def get_time(self, value):
        if not value:
            return ""
        dt = self.to_tz_date(value)
        return dtime.date_to_string(dt, "%H:%M")

    def get_max(self):
        now = DateTime()
        return now.strftime("%Y-%m-%d")

    def get_min(self):
        now = DateTime()
        return now.strftime("%Y-%m-%d")

    def attrs(self, context):
        min_date = self.get_min_date(context)
        max_date = self.get_max_date(context)
        return {
            "min": dtime.date_to_string(min_date),
            "max": dtime.date_to_string(max_date),
        }

    def get_min_date(self, instance):
        """Returns the minimum datetime supported by this widget and instance
        """
        return self.to_date(self.min, instance, dtime.datetime.min)

    def get_max_date(self, instance):
        """Returns the maximum datetime supported for this widget and instance
        """
        return self.to_date(self.max, instance, dtime.datetime.max)

    def to_date(self, thing, instance, default):
        """Resolves the thing passed in to a DateTime object or None
        """
        if not thing:
            return default

        date = api.to_date(thing)
        if api.is_date(date):
            return date

        if api.is_string(thing) and thing in ["current", "now"]:
            return dtime.datetime.now()

        if callable(thing):
            value = thing()
            return self.to_date(value, instance, default)

        if hasattr(instance, thing):
            value = getattr(instance, thing)
            return self.to_date(value, instance, default)

        if api.is_string(thing):
            obj = api.get_object(instance, None)
            fields = obj and api.get_fields(instance) or {}
            field = fields.get(thing)
            if field:
                value = field.get(instance)
                return self.to_date(value, instance, default)

        return default


registerWidget(
    DateTimeWidget,
    title="DateTimeWidget",
    description=("Simple text field, with a jquery date widget attached.")
)

registerPropertyType("show_time", "boolean")
