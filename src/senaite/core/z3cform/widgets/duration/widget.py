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

from datetime import timedelta

from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IDurationField
from senaite.core.z3cform.interfaces import IDurationWidget
from senaite.core.z3cform.widgets.basewidget import BaseWidget
from z3c.form.browser import widget
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.converter import TimedeltaDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer


@adapter(IDurationField, IDurationWidget)
class DurationDataConverter(TimedeltaDataConverter):
    """Converts the value between the field and the widget
    """

    def toWidgetValue(self, value):
        """Converts from field value to widget
        """
        if not isinstance(value, timedelta):
            return {}

        # Note timedelta keeps days and seconds a part!
        return {
            "days": value.days,
            "hours": (value.seconds / 3600) % 24, # hours within a day
            "minutes": (value.seconds / 60) % 60, # minutes within an hour
            "seconds": value.seconds % 60, # seconds within a minute
        }

    def toFieldValue(self, value):
        """Converts from widget to field value
        """
        return timedelta(**value)


@implementer(IDurationWidget)
class DurationWidget(HTMLInputWidget, BaseWidget):
    """Widget for duration in days, hours, minutes and seconds
    """
    klass = u"senaite-duration-widget"

    # Basic properties
    show_days = True
    show_hours = True
    show_minutes = True
    show_seconds = False

    def update(self):
        """Computes self.value for the widget templates

        see z3c.form.widget.Widget
        """
        super(DurationWidget, self).update()
        widget.addFieldClass(self)


@adapter(IDurationField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def DurationWidgetFactory(field, request):
    """Widget factory for duration field
    """
    return FieldWidget(field, DurationWidget(request))
