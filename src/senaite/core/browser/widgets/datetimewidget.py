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

from bika.lims import api
from AccessControl import ClassSecurityInfo
from bika.lims.browser import ulocalized_time as ut
from DateTime import DateTime
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

    def isoformat(self, time, context, request):
        dt = api.to_date(time)
        if self.show_time:
            return dt.ISO8601()
        return dt.strftime("%Y-%m-%d")

    def today(self, offset=0):
        now = DateTime() + offset
        if self.show_time:
            return now.ISO8601()
        return now.strftime("%Y-%m-%d")

    def attrs(self):
        attrs = {}
        if self.show_time:
            attrs["pattern"] = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}"
        else:
            attrs["pattern"] = r"\d{4}-\d{2}-\d{2}}"
        if self.datepicker_nofuture:
            attrs["max"] = self.today()
        if self.datepicker_nopast:
            attrs["min"] = self.today()
        return attrs


registerWidget(
    DateTimeWidget,
    title="DateTimeWidget",
    description=("Simple text field, with a jquery date widget attached.")
)

registerPropertyType("show_time", "boolean")
