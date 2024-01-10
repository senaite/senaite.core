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
        self.toggle_price_vat_fields(False)
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")
        if name == "UseAnalysisProfilePrice":
            self.toggle_price_vat_fields(value)
        return self.data

    def toggle_price_vat_fields(self, toggle=False):
        if toggle:
            self.add_show_field("AnalysisProfilePrice")
            self.add_show_field("AnalysisProfileVAT")
        else:
            self.add_hide_field("AnalysisProfilePrice")
            self.add_hide_field("AnalysisProfileVAT")
