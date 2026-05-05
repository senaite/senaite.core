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
from senaite.core.browser.form.helpers import get_form_value
from senaite.core.browser.form.helpers import has_form_field
from senaite.core.browser.form.helpers import is_checked

HAZARDOUS_FIELD = "Hazardous"
HAZARD_CATEGORIES_FIELD = "HazardCategories"


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Reference Definitions"""

    def _toggle_hazard_categories(self, hazardous):
        if hazardous:
            self.add_show_field(HAZARD_CATEGORIES_FIELD)
        else:
            self.add_hide_field(HAZARD_CATEGORIES_FIELD)

    def initialized(self, data):
        form = data.get("form") or {}
        if has_form_field(form, HAZARDOUS_FIELD):
            hazardous = is_checked(get_form_value(form, HAZARDOUS_FIELD))
        else:
            hazardous = bool(self.context.getHazardous())
        self._toggle_hazard_categories(hazardous)
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")
        if name == HAZARDOUS_FIELD:
            self._toggle_hazard_categories(is_checked(value))
        return self.data
