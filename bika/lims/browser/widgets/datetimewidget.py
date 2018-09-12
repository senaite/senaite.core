# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import datetime
from time import strptime

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from bika.lims import logger
from Products.ATContentTypes.utils import dt2DT
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
        if not time:
            return ""
        if isinstance(time, basestring):
            dtime = self.get_datetime_from_locale_format(context, time)
            return self.ulocalized_time(dt2DT(dtime), context, request)

        # DateTime is stored with TimeZone, but widget omits TZ!
        dtime = time.toZone("GMT+0")
        return ut(dtime,
                 long_format=self.show_time,
                 time_only=False,
                 context=context,
                 request=request)

    def get_datetime_from_locale_format(self, instance, date_string):
        """Converts a date string to a datetime object
        """
        default_format = "%Y-%m-%d"
        locale_key = "date_format_short"
        if self.show_time:
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


    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Basic impl for form processing in a widget"""
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker
        return value, {}


registerWidget(
    DateTimeWidget,
    title='DateTimeWidget',
    description=('Simple text field, with a jquery date widget attached.')
)

registerPropertyType('show_time', 'boolean')
