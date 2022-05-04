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
            method_uid = value[0]
            options = self.get_instruments_options(method_uid)
            self.add_update_field("Instrument", {"options": options})

        return self.data

    def get_instruments_options(self, method):
        """Returns a list of dicts that represent instrument options suitable
        for a selection list, with an empty option as first item
        """
        options = [{"title": _("No Instrument"), "value": [""]}]
        method = api.get_object(method, default=None)
        instruments = method and method.getInstruments() or []
        for instrument in instruments:
            option = {
                "title": api.get_title(instrument),
                "value": api.get_uid(instrument)
            }
            options.append(option)

        return options
