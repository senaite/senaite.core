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

    def _validate(self, value):
        super(CoordinateField, self)._validate(value)


class LatitudeCoordinateField(CoordinateField):
    """A field that handles latitude coordinates (deg, min, sec, bearing)
    """
    bearing = list("NS")


class LongitudeCoordinateField(CoordinateField):
    """A field that handles longitude coordinates (deg, min, sec, bearing)
    """
    bearing = list("WE")
