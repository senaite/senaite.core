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
from senaite.core.i18n import translate as t
from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import ICoordinateField
from zope.interface import implementer
from zope.schema import Dict


SUBFIELDS = ("degrees", "minutes", "seconds", "bearing")


@implementer(ICoordinateField)
class CoordinateField(Dict, BaseField):
    """A field that handles location coordinates (deg, min, sec, bearing)
    """
    bearing = list("NSWE")

    def __init__(self, **kwargs):
        default = kwargs.get("default")
        kwargs["default"] = default or dict.fromkeys(SUBFIELDS, "")
        super(CoordinateField, self).__init__(**kwargs)

    def set(self, object, value):
        """Set the coordinate field value
        """
        # ensure the value is a valid dict
        coordinate = copy.deepcopy(self.default)
        if value:
            coordinate.update(value)

        # convert values to strings preserving the whole fraction, if any
        for key in coordinate.keys():
            val = coordinate[key]
            coordinate[key] = api.float_to_string(val, default=val)

        # store the value
        super(CoordinateField, self).set(object, coordinate)

    def _validate(self, value):
        super(CoordinateField, self)._validate(value)

        # check minutes are within 0 and 59
        minutes = value.get("minutes", 0)
        minutes = api.to_int(minutes, default=0)
        if minutes < 0 or minutes > 59:
            msg = t(_("Value for minutes must be within 0 and 59"))
            raise ValueError(msg)

        # check seconds are within 0 and 59.9999. With 4 decimal places, the
        # max precision is ~100mm (individual humans can be unambiguously
        # recognized at this scale)
        seconds = value.get("seconds", 0)
        seconds = api.to_float(seconds, default=0)
        if seconds < 0 or seconds >= 60:
            msg = t(_("Value for seconds must be within 0 and 59.9999"))
            raise ValueError(msg)


class LatitudeCoordinateField(CoordinateField):
    """A field that handles latitude coordinates (deg, min, sec, bearing)
    """
    bearing = list("NS")

    def _validate(self, value):
        super(LatitudeCoordinateField, self)._validate(value)

        # check degrees are within 0 and 90
        degrees = value.get("degrees")
        degrees = api.to_int(degrees, default=0)
        if degrees < 0 or degrees > 90:
            msg = t(_("Value for degrees must be within 0 and 90"))
            raise ValueError(msg)


class LongitudeCoordinateField(CoordinateField):
    """A field that handles longitude coordinates (deg, min, sec, bearing)
    """
    bearing = list("WE")

    def _validate(self, value):
        super(LongitudeCoordinateField, self)._validate(value)

        # check degrees are within 0 and 180
        degrees = value.get("degrees")
        degrees = api.to_int(degrees, default=0)
        if degrees < 0 or degrees > 180:
            msg = t(_("Value for degrees must be within 0 and 180"))
            raise ValueError(msg)
