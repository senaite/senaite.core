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
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from senaite.core.browser.form.adapters import EditFormAdapterBase
from senaite.core.interfaces import IAjaxEditForm
from zope.component import queryMultiAdapter


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Worksheet Template
    """

    def initialized(self, data):
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # Handle Methods Change
        if name == "RestrictToMethod" and value:
            value = value[0]
            empty = [{"title": _("No Instrument"), "value": [""]}]
            if not api.is_uid(value):
                self.add_update_field("Instruments:list", {
                    "options": empty})
                self.add_update_field("Instruments_options", {
                    "options": empty})
                self.add_update_field("Instrument", {
                    "options": empty})
                return self.data

            # Get selected method
            method = api.get_object_by_uid(value)
            instruments = method.getInstruments()
            i_opts = map(lambda o: dict(
                title=api.get_title(o), value=api.get_uid(o)), instruments)

            i_sel = map(api.get_uid, instruments)
            self.add_update_field("Instruments_options", {
                "options": i_opts})
            self.add_update_field("Instruments:list", {
                "options": i_opts, "selected": i_sel})
            self.add_update_field("Instrument", {
                "options": empty + i_opts})

        return self.data
