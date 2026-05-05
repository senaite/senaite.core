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
from senaite.core.interfaces import ISampleType
from senaite.core.vocabularies.stickers import get_sticker_templates

_DGF_WIDGET_PREFIX = "form.widgets.admitted_sticker_templates.0.widgets."

HAZARDOUS_FIELD = "form.widgets.hazardous"
HAZARD_CATEGORIES_FIELD = "form.widgets.hazard_categories"


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Sample Type
    """

    def _toggle_hazard_categories(self, hazardous):
        """Show or hide the hazard_categories field."""
        if hazardous:
            self.add_show_field(HAZARD_CATEGORIES_FIELD)
        else:
            self.add_hide_field(HAZARD_CATEGORIES_FIELD)

    def initialized(self, data):
        # Read the currently-submitted form state when present so the
        # toggle survives a re-render after validation errors. Falls
        # back to the persisted context value on the initial render.
        form = data.get("form") or {}
        if has_form_field(form, HAZARDOUS_FIELD):
            hazardous = is_checked(get_form_value(form, HAZARDOUS_FIELD))
        elif ISampleType.providedBy(self.context):
            hazardous = bool(self.context.getHazardous())
        else:
            hazardous = False
        self._toggle_hazard_categories(hazardous)
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # toggle hazard categories visibility with the Hazardous flag
        if name == HAZARDOUS_FIELD:
            self._toggle_hazard_categories(is_checked(value))
            return self.data

        # filter default small/large sticker
        if name == _DGF_WIDGET_PREFIX + "admitted":
            # get the sticker
            templates = filter(
                lambda t: t.get("id") in value, get_sticker_templates())

            # prepare options for the select field
            opts = map(lambda t: dict(
                title=t.get("title"), value=t.get("id")), templates)

            default_small = default_large = None
            if ISampleType.providedBy(self.context):
                default_small = self.context.getDefaultSmallSticker()
                default_large = self.context.getDefaultLargeSticker()

            # set default small sticker
            self.add_update_field(_DGF_WIDGET_PREFIX + "small_default", {
                "selected": [default_small] if default_small else [],
                "options": opts})

            # set default large sticker
            self.add_update_field(_DGF_WIDGET_PREFIX + "large_default", {
                "selected": [default_large] if default_large else [],
                "options": opts})

        return self.data
