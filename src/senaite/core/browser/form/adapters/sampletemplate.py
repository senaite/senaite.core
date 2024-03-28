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
    """Edit form adapter for DX Sample Template
    """
    def initialized(self, data):
        # form = data.get("form", {})
        # for k, v in form.items():
        #     if k.endswith("part_id"):
        #         self.add_attribute("input[name='%s']" % k, "readonly", "1")
        return self.data

    def modified(self, data):
        form = data.get("form", {})
        partitions = []
        for k, v in form.items():
            if k.endswith("part_id"):
                partitions.append((k, v), )
        for num, part in enumerate(sorted(partitions, key=lambda x: x[0])):
            self.add_update_field(part[0], "part-%s" % str(num + 1))
        return self.data
