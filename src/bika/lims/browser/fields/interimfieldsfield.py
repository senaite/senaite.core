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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import copy

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from Products.Archetypes import DisplayList
from Products.Archetypes.Registry import registerField
from senaite.core.browser.fields.records import RecordsField


class InterimFieldsField(RecordsField):
    """a list of InterimFields for calculations """
    _properties = RecordsField._properties.copy()
    _properties.update({
        "fixedSize": 0,
        "minimalSize": 0,
        "maximalSize": 9999,
        "type": "InterimFields",
        "subfields": (
            "keyword",
            "title",
            "value",
            "choices",
            "result_type",
            "allow_empty",
            "unit",
            "report",
            "hidden",
            "wide"
        ),
        "required_subfields": ("keyword", "title"),
        "subfield_labels": {
            "keyword": _("Keyword"),
            "title": _("Field Title"),
            "value": _("Default value"),
            "choices": _("Choices"),
            "result_type": _("Control type"),
            "allow_empty": _("Allow empty"),
            "unit": _("Unit"),
            "report": _("Report"),
            "hidden": _("Hidden Field"),
            "wide": _("Apply wide"),
        },
        "subfield_descriptions": {
            "result_type": _(
                "Type of control to be displayed on value entry when choices "
                "are set")
        },
        "subfield_types": {
            "hidden": "boolean",
            "value": "string",
            "choices": "string",
            "result_type": "selection",
            "allow_empty": "boolean",
            "wide": "boolean",
            "report": "boolean",
        },
        "subfield_sizes": {
            "keyword": 20,
            "title": 20,
            "value": 10,
            "choices": 50,
            "result_type": 1,
            "unit": 10,
        },
        "subfield_maxlength": {
            "choices": -1,
        },
        "subfield_validators": {
            "keyword": "interimfieldsvalidator",
            "title": "interimfieldsvalidator",
            "value": "interimfieldsvalidator",
            "unit": "interimfieldsvalidator",
            "choices": "interimfieldsvalidator",
            "result_type": "interimfieldsvalidator",
        },
        "subfield_vocabularies": {
            "result_type": DisplayList((
                ("", _("Numeric")),
                ("string", _("String")),
                ("text", _("Text")),
                ("datetime", _("Datetime")),
                ("select", _("Selection list")),
                ("multiselect", _("Multiple selection")),
                ("multiselect_duplicates", _(
                    "Multiple selection (with duplicates)"
                )),
                ("multichoice", _("Multiple choices")),
                ("multivalue", _("Multiple values")),
            )),
        },
    })
    security = ClassSecurityInfo()

    def get(self, instance, **kwargs):
        # local set interims
        interims = RecordsField.get(self, instance, **kwargs) or []

        # make sure we have a copy of the interims field
        return copy.deepcopy(interims)

    def set(self, instance, value, **kwargs):
        RecordsField.set(self, instance, value, **kwargs)


registerField(
    InterimFieldsField,
    title="Interim Fields",
    description="Used for storing Interim Fields or Interim Results")
