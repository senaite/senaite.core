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

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from senaite.core.browser.form.adapters import EditFormAdapterBase


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Lab Contact
    """

    def initialized(self, data):
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # Populate the default department
        if name == "Departments":
            departments = map(api.get_object_by_uid, value)
            default_dpt = self.context.getDefaultDepartment()
            empty = [{"title": _(""), "value": None}]
            opts = map(lambda o: dict(
                title=api.get_title(o), value=api.get_uid(o)), departments)
            self.add_update_field("DefaultDepartment", {
                "selected": [api.get_uid(default_dpt)] if default_dpt else [],
                "options": empty + opts})

        return self.data
