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

from bika.lims import _
from bika.lims import api
from senaite.core.browser.form.adapters import EditFormAdapterBase
from senaite.core.browser.form.helpers import get_form_value
from senaite.core.browser.form.helpers import has_form_field
from senaite.core.browser.form.helpers import is_checked

HAZARDOUS_FIELD = "Hazardous"
HAZARD_CATEGORIES_FIELD = "HazardCategories"


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Reference Samples
    """

    def _toggle_hazard_categories(self, hazardous):
        if hazardous:
            self.add_show_field(HAZARD_CATEGORIES_FIELD)
        else:
            self.add_hide_field(HAZARD_CATEGORIES_FIELD)

    def initialized(self, data):
        # disable ManualID if necessary
        if self.context.objectIds():
            self.add_readonly_field(
                "ManualId", _(
                    "The Reference Sample ID cannot be changed because it is "
                    "already associated with other objects, such as QC "
                    "analyses.",
                )
            )
        # Read live form state so the toggle survives a re-render
        # after validation errors. Falls back to the persisted value.
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

        # toggle hazard categories visibility with the Hazardous flag
        if name == HAZARDOUS_FIELD:
            self._toggle_hazard_categories(is_checked(value))
            return self.data

        # Populate dependencies of the reference definition
        if name == "ReferenceDefinition":
            definitions = map(api.get_object_by_uid, filter(api.is_uid, value))
            if len(definitions) > 0:
                definition = definitions[0]
                self.add_update_field("Hazardous", definition.getHazardous())
                self.add_update_field("Blank", definition.getBlank())

                # set reference results
                selected = []
                records = definition.getReferenceResults()
                for rec in records:
                    uid = rec.get("uid")
                    selected.append(uid)
                    self.add_update_field("result.%s" % uid, rec.get("result"))
                    self.add_update_field("min.%s" % uid, rec.get("min"))
                    self.add_update_field("max.%s" % uid, rec.get("max"))
                    self.add_update_field("error.%s" % uid, rec.get("error"))

                self.add_state_listing("list", selected_uids=selected)
