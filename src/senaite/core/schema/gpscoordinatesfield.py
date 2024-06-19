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

import copy

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from senaite.core.api import geo
from senaite.core.i18n import translate as t
from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import IGPSCoordinatesField
from zope.interface import implementer
from zope.schema import Dict

SUBFIELDS = ("latitude", "longitude")

# One meter resolution ~ 5 decimal places
# ~11 centimeter resolution ~ 6 decimal places
# One centimeter resolution ~ 7 decimal places
# One millimeter resolution ~ 8 decimal places
# https://xkcd.com/2170/
DEFAULT_PRECISION = 7


@implementer(IGPSCoordinatesField)
class GPSCoordinatesField(Dict, BaseField):
    """A field that handles GPS coordinates
    """

    def __init__(self, **kwargs):
        default = kwargs.get("default")
        kwargs["default"] = default or dict.fromkeys(SUBFIELDS, "")
        super(GPSCoordinatesField, self).__init__(**kwargs)
        self.precision = kwargs.get("precision") or DEFAULT_PRECISION

    def set(self, object, value):
        """Set the GPS coordinates field value
        """
        if not value:
            value = {}

        if not isinstance(value, dict):
            raise TypeError("Expected value to be a 'dict', but got %r" %
                            type(value))

        # ensure the value is a valid dict
        coordinates = copy.deepcopy(self.default)
        if isinstance(value, dict):
            coordinates.update(value)

        # call the validator
        self._validate(coordinates)

        # check the type of the precision
        if not isinstance(self.precision, int):
            raise TypeError("Expected precision to be 'int', but got %r" %
                            type(self.precision))

        # convert values to strings with the right precision
        template = "{:.%df}" % self.precision
        for key in coordinates.keys():

            # handle DMS-like values
            val = geo.to_decimal_degrees(coordinates[key],
                                         precision=self.precision,
                                         default=coordinates[key])

            # skip non-floatable (eg. empties)
            if not api.is_floatable(val):
                continue

            # update to right precision
            val = api.to_float(val)
            coordinates[key] = template.format(val)

        # store the value
        super(GPSCoordinatesField, self).set(object, coordinates)

    def _validate(self, value):
        """Validator called on form submit
        """
        # check latitude degrees are within range
        lat = value.get("latitude", 0)
        lat = api.to_float(lat, default=0)
        if abs(lat) > 90:
            msg = t(_("Latitude must be within -90 and 90 degrees"))
            raise ValueError(msg)

        # check longitude degrees are within range
        lon = value.get("longitude", 0)
        lon = api.to_float(lon, default=0)
        if abs(lon) > 180:
            msg = t(_("Longitude must be within -180 and 180 degrees"))
            raise ValueError(msg)
