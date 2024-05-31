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

from senaite.core.api import geo
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IGPSCoordinatesField
from senaite.core.z3cform.interfaces import IGPSCoordinatesWidget
from senaite.core.z3cform.widgets.basewidget import BaseWidget
from z3c.form.browser import widget
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer

DEFAULT_LAYER = "osm"

DEFAULT_ZOOM = 17

LAYER_TEMPLATES = (
    ("osm", "https://osm.org/?mlat={latitude}&mlon={longitude}&zoom={zoom}"),
    ("google", "https://maps.google.com/?q={latitude},{longitude}&z={zoom}"),
)


@adapter(IGPSCoordinatesField, IGPSCoordinatesWidget)
class GPSCoordinatesDataConverter(BaseDataConverter):
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


@implementer(IGPSCoordinatesWidget)
class GPSCoordinatesWidget(HTMLInputWidget, BaseWidget):
    """Widget for GPS coordinates in latitude and longitude
    """
    klass = u"senaite-gps-coordinates-widget"

    def __init__(self, request, layer=DEFAULT_LAYER, zoom=DEFAULT_ZOOM):
        super(GPSCoordinatesWidget, self).__init__(request)
        self.request = request
        self.layer = layer
        self.zoom = zoom

    @property
    def step(self):
        """Returns the step to apply to html input elements
        """
        template = "{:.%df}" % self.field.precision
        return "%s1" % template.format(0)[:-1]

    def get_map_url(self):
        """Returns the url to the map provider
        """
        template = dict(LAYER_TEMPLATES).get(self.layer, "")
        return template.format(zoom=self.zoom, **self.value)

    def get_dms(self):
        """Returns the value as DMS
        """
        latitude = self.value.get("latitude")
        longitude = self.value.get("longitude")
        return {
            "latitude": geo.to_latitude_dms(latitude, default=None),
            "longitude": geo.to_longitude_dms(longitude, default=None)
        }

    def update(self):
        """Computes self.value for the widget templates

        see z3c.form.widget.Widget
        """
        super(GPSCoordinatesWidget, self).update()
        widget.addFieldClass(self)


@adapter(IGPSCoordinatesField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def GPSCoordinatesWidgetFactory(field, request):
    """Widget factory for GPSCoordinates field
    """
    return FieldWidget(field, GPSCoordinatesWidget(request))
