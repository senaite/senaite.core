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

from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import ICoordinateField
from senaite.core.z3cform.interfaces import ICoordinateWidget
from senaite.core.z3cform.widgets.basewidget import BaseWidget
from z3c.form.browser import widget
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer


@adapter(ICoordinateField, ICoordinateWidget)
class CoordinateDataConverter(BaseDataConverter):
    """Converts the value between the field and the widget
    """

    def toWidgetValue(self, value):
        """Converts from field value to widget
        """
        if not isinstance(value, dict):
            return {}
        return value

    def toFieldValue(self, value):
        """Converts from widget to field value
        """
        if not isinstance(value, dict):
            return {}
        return value


@implementer(ICoordinateWidget)
class CoordinateWidget(HTMLInputWidget, BaseWidget):
    """Widget for coordinate in degrees, minutes, seconds and bearing
    """
    klass = u"senaite-coordinate-widget"

    @property
    def bearing_options(self):
        return self.field.bearing

    def update(self):
        """Computes self.value for the widget templates

        see z3c.form.widget.Widget
        """
        super(CoordinateWidget, self).update()
        widget.addFieldClass(self)


@adapter(ICoordinateField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def CoordinateWidgetFactory(field, request):
    """Widget factory for coordinate field
    """
    return FieldWidget(field, CoordinateWidget(request))
