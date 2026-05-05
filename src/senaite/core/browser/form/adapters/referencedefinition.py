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

from senaite.core.browser.form.adapters import EditFormAdapterBase

HAZARDOUS_FIELD = "Hazardous"
HAZARD_CATEGORIES_FIELD = "HazardCategories"


def _is_truthy(value):
    """Return True if the form value represents a checked boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, tuple)):
        return any(_is_truthy(v) for v in value)
    return str(value).lower() in ("true", "1", "selected", "on")


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Reference Definitions"""

    def _toggle_hazard_categories(self, hazardous):
        if hazardous:
            self.add_show_field(HAZARD_CATEGORIES_FIELD)
        else:
            self.add_hide_field(HAZARD_CATEGORIES_FIELD)

    def initialized(self, data):
        self._toggle_hazard_categories(bool(self.context.getHazardous()))
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")
        if name == HAZARDOUS_FIELD:
            self._toggle_hazard_categories(_is_truthy(value))
        return self.data
