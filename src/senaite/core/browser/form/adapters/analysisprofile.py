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

from senaite.core.browser.form.adapters import EditFormAdapterBase


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Analysis Profiles
    """

    def initialized(self, data):
        if not self.use_profile_price(data.get("form", {})):
            self.toggle_price_vat_fields(False)
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")
        if name == "form.widgets.use_analysis_profile_price":
            self.toggle_price_vat_fields(value)
        return self.data

    def use_profile_price(self, form):
        value = form.get("form.widgets.use_analysis_profile_price:list")
        return value == "selected"

    def toggle_price_vat_fields(self, toggle=False):
        if toggle:
            self.add_show_field("form.widgets.analysis_profile_price")
            self.add_show_field("form.widgets.analysis_profile_vat")
        else:
            self.add_hide_field("form.widgets.analysis_profile_price")
            self.add_hide_field("form.widgets.analysis_profile_vat")
