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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from bika.lims.browser import get_date
from bika.lims.browser import ulocalized_time as ut


class DateTimeWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'show_time': False,
        'macro': "bika_widgets/datetimewidget",
        'helper_js': ("bika_widgets/datetimewidget.js",),
        'helper_css': ("bika_widgets/datetimewidget.css",),
    })

    security = ClassSecurityInfo()

    def ulocalized_time(self, time, context, request):
        """Returns the localized time in string format
        """
        value = ut(time, long_format=self.show_time, time_only=False,
                   context=context, request=request)
        return value or ""

    def ulocalized_gmt0_time(self, time, context, request):
        """Returns the localized time in string format, but in GMT+0
        """
        value = get_date(context, time)
        if not value:
            return ""
        # DateTime is stored with TimeZone, but DateTimeWidget omits TZ
        value = value.toZone("GMT+0")
        return self.ulocalized_time(value, context, request)


registerWidget(
    DateTimeWidget,
    title='DateTimeWidget',
    description=('Simple text field, with a jquery date widget attached.')
)

registerPropertyType('show_time', 'boolean')
