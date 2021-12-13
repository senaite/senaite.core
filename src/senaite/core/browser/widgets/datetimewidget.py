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

from AccessControl import ClassSecurityInfo
from bika.lims.browser import ulocalized_time as ut
from DateTime import DateTime
from DateTime.DateTime import safelocaltime
from DateTime.interfaces import DateTimeError
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget


class DateTimeWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        "show_time": False,
        "datepicker_nofuture": False,
        "datepicker_nopast": False,
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
            return dt.strftime("%Y-%m-%dT%H:%M")
        return dt.strftime("%Y-%m-%d")

    def get_date(self, value):
        if not value:
            return ""
        dt = self.to_tz_date(value)
        return dt.strftime("%Y-%m-%d")

    def get_time(self, value):
        if not value:
            return ""
        dt = self.to_tz_date(value)
        return dt.strftime("%H:%M")

    def get_max(self):
        now = DateTime()
        return now.strftime("%Y-%m-%d")

    def get_min(self):
        now = DateTime()
        return now.strftime("%Y-%m-%d")

    def attrs(self):
        attrs = {}
        if self.datepicker_nofuture:
            attrs["max"] = self.get_max()
        if self.datepicker_nopast:
            attrs["min"] = self.get_min()
        return attrs


registerWidget(
    DateTimeWidget,
    title="DateTimeWidget",
    description=("Simple text field, with a jquery date widget attached.")
)

registerPropertyType("show_time", "boolean")
