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
from bika.lims import bikaMessageFactory as _
from Products.Archetypes.Registry import registerField
from senaite.core.browser.fields.record import RecordField


class CoordinateField(RecordField):
    """Stores angle in deg, min, sec, bearing
    """
    security = ClassSecurityInfo()
    _properties = RecordField._properties.copy()
    _properties.update({
        "type": "angle",
        "subfields": ("degrees", "minutes", "seconds", "bearing"),
        "subfield_labels": {
            "degrees": _("Degrees"),
            "minutes": _("Minutes"),
            "seconds": _("Seconds"),
            "bearing": _("Bearing")},
        "subfield_sizes": {
            "degrees": 3,
            "minutes": 2,
            "seconds": 2,
            "bearing": 1},
        "subfield_validators": {
            "degrees": "coordinatevalidator",
            "minutes": "coordinatevalidator",
            "seconds": "coordinatevalidator",
            "bearing": "coordinatevalidator",
        },
    })


registerField(CoordinateField,
              title="Coordinate",
              description="Used for storing coordinates")
