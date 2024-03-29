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

from bika.lims import api
from senaite.core.browser.form.adapters import EditFormAdapterBase
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.interfaces import ISampleTemplate

RX1 = r"\d+\.(widgets)\.(part_id)"
RX2 = r"\.(widgets)\.(part_id)"


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

        # get the current selected services of the context
        services = self.get_current_services()

        # iterate over all service UIDs to fill the partition selectors with
        # the current (unsaved) partition scheme
        for uid in self.get_all_service_uids():
            fieldname = "Partition.{}:records".format(uid)
            selected = services.get(uid)
            part_id = None
            if selected:
                part_id = selected.get("part_id")
            self.add_update_field(fieldname, {
                "selected": [part_id] if part_id else [],
                "options": empty + opts})
        return self.data

    def callback(self, data):
        name = data.get("name")
        if not name:
            return
        method = getattr(self, name, None)
        if not callable(method):
            return
        return method(data)

    def get_current_services(self):
        """Get the current service settings
        """
        if not ISampleTemplate.providedBy(self.context):
            return {}
        services = {}
        for service in self.context.getServices():
            uid = service.get("uid")
            services[uid] = service
        return services

    def get_all_service_uids(self):
        """Return all service
        """
        query = {
            "portal_type": "AnalysisService",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        results = api.search(query, SETUP_CATALOG)
        return list(map(api.get_uid, results))

    def get_current_partition_ids(self, data, only_numbered=False):
        """Get the current unique partition IDs from the request

        :returns: list of unique parition IDs
        """
        form = data.get("form")
        if (only_numbered):
            partitions = [(k, v) for k, v in form.items() if re.search(RX1, k)]
        else:
            partitions = [(k, v) for k, v in form.items() if re.search(RX2, k)]
        return list(set(dict(partitions).values()))

    def get_current_partition_count(self, data):
        """Count the current unique partition IDs

        :returns: Number of rows containing a unique Partition ID
        """
        unique_ids = self.get_current_partition_ids(data)
        return len(unique_ids)

    def on_partition_added(self, data):
        """Handle new partition rows
        """
        count = self.get_current_partition_count(data)
        # we just want to get the next ID right
        self.add_update_field(
            "form.widgets.partitions.AA.widgets.part_id",
            "part-{}".format(count + 1))
        return self.data

    def on_partition_removed(self, data):
        """Handle removed partition rows
        """
        count = self.get_current_partition_count(data)
        # we just want to get the next ID right
        self.add_update_field(
            "form.widgets.partitions.AA.widgets.part_id",
            "part-{}".format(count))
        return self.data
