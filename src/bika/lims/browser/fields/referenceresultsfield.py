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
from senaite.core.browser.fields.records import RecordsField


class ReferenceResultsField(RecordsField):
    """a list of reference sample results """
    _properties = RecordsField._properties.copy()
    _properties.update({
        "type": "referenceresult",
        "subfields": ("uid", "result", "min", "max", "error"),
        "subfield_labels": {
            "uid": _("Analysis Service"),
            "result": _("Expected Result"),
            "error": _("Permitted Error %"),
            "min": _("Min"),
            "max": _("Max")},
        })
    security = ClassSecurityInfo()


registerField(ReferenceResultsField,
              title="Reference Values",
              description="Used for storing reference results")
