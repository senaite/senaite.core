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

import re
from senaite.core.browser.form.adapters import EditFormAdapterBase

RX = r"\.(widgets)\.(part_id)"


class EditForm(EditFormAdapterBase):
    """Edit form adapter for DX Sample Template
    """
    def initialized(self, data):
        # register callbacks
        self.add_callback("body",
                          "datagrid:row_added",
                          "on_partition_added")
        self.add_callback("body",
                          "datagrid:row_removed",
                          "on_partition_removed")
        self.add_callback("select[name^='Partition'][name$=':records']",
                          "click",
                          "on_partition_select")

        # handle additional rendered row on edit view
        if self.get_current_partition_count(data) > 1:
            self.on_partition_added(data)
        return self.data

    def modified(self, data):
        return self.data

    def added(self, data):
        empty = [{"title": "", "value": ""}]
        opts = map(lambda o: dict(title=o, value=o),
                   self.get_current_partition_ids(data, only_numbered=True))
        for uid in self.get_service_uids():
            fieldname = "Partition.{}:records".format(uid)
            self.add_update_field(fieldname, {"options": empty + opts})
        return self.data

    def callback(self, data):
        name = data.get("name")
        if not name:
            return
        method = getattr(self, name, None)
        if not callable(method):
            return
        return method(data)

    def get_current_partition_ids(self, data):
        """Get the current unique IDs

        :returns: list of unique parition IDs
        """
        form = data.get("form")
        partitions = [(k, v) for k, v in form.items() if re.search(RX, k)]
        return list(set(dict(partitions).values()))

    def get_current_partition_count(self, data):
        """Count the current unique IDs

        :returns: Number of rows containing a unique Partition ID
        """
        unique_ids = self.get_current_partition_ids(data)
        return len(unique_ids)

    def on_partition_added(self, data):
        """A new partition was added
        """
        count = self.get_current_partition_count(data)
        # we just want to get the next ID right
        self.add_update_field(
            "form.widgets.partitions.AA.widgets.part_id",
            "part-{}".format(count + 1))
        return self.data

    def on_partition_removed(self, data):
        """An existing partition was deleted
        """
        count = self.get_current_partition_count(data)
        # we just want to get the next ID right
        self.add_update_field(
            "form.widgets.partitions.AA.widgets.part_id",
            "part-{}".format(count))
        return self.data

    def on_partition_select(self, data):
        import pdb; pdb.set_trace()
        return self.data
