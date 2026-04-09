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

import collections

from bika.lims import bikaMessageFactory as _
from bika.lims.config import MAX_OPERATORS
from bika.lims.config import MIN_OPERATORS
from bika.lims.utils import to_choices
from senaite.core.permissions import FieldEditSpecification
from bika.lims.api.security import check_permission

from .services_widget import ServicesWidget


class AnalysisSpecServicesWidget(ServicesWidget):
    """Listing widget for Analysis Specification Services
    """

    def update(self):
        super(AnalysisSpecServicesWidget, self).update()
        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Service"),
                "index": "sortable_title",
                "sortable": False
            }),
            ("Keyword", {
                "title": _("Keyword"),
                "sortable": False
            }),
            ("Methods", {
                "title": _("Methods"),
                "sortable": False
            }),
            ("Unit", {
                "title": _("Unit"),
                "sortable": False
            }),
            ("warn_min", {
                "title": _("Min warn"),
                "sortable": False,
                "type": "numeric",
            }),
            ("min", {
                "title": _("Min"),
                "sortable": False,
                "type": "numeric",
            }),
            ("min_operator", {
                "title": _("Min operator"),
                "type": "choices",
                "sortable": False,
            }),
            ("max", {
                "title": _("Max"),
                "sortable": False,
                "type": "numeric",
            }),
            ("warn_max", {
                "title": _("Max warn"),
                "sortable": False,
                "type": "numeric",
            }),
            ("max_operator", {
                "title": _("Max operator"),
                "type": "choices",
                "sortable": False,
            }),
            ("hidemin", {
                "title": _("< Min"),
                "sortable": False,
                "type": "numeric",
            }),
            ("hidemax", {
                "title": _("> Max"),
                "sortable": False,
                "type": "numeric",
            }),
            ("rangecomment", {
                "title": _(u"Out of range comment"),
                "sortable": False,
                "type": "string",
            }),
        ))

        self.review_states[0]["columns"] = self.columns.keys()

    def folderitem(self, obj, item, index):
        item = super(AnalysisSpecServicesWidget,
                     self).folderitem(obj, item, index)

        uid = item.get("uid")

        # Get existing record data from the field (results_range)
        # Note: self.records is populated
        # by DefaultListingWidget from the field value
        record = self.records.get(uid, {})

        item["min"] = record.get("min", "")
        item["max"] = record.get("max", "")
        item["warn_min"] = record.get("warn_min", "")
        item["warn_max"] = record.get("warn_max", "")
        item["hidemin"] = record.get("hidemin", "")
        item["hidemax"] = record.get("hidemax", "")
        item["rangecomment"] = record.get("rangecomment", "")

        if "choices" not in item:
            item["choices"] = {}
        item["choices"]["min_operator"] = to_choices(MIN_OPERATORS)
        item["choices"]["max_operator"] = to_choices(MAX_OPERATORS)

        max_op = record.get("max_operator", "leq")
        min_op = record.get("min_operator", "geq")

        can_edit = check_permission(FieldEditSpecification, self.context)

        if can_edit:
            item["max_operator"] = max_op
            item["min_operator"] = min_op
            item["allow_edit"] = [
                "min", "max", "warn_min", "warn_max", 
                "hidemin", "hidemax", "rangecomment", 
                "min_operator", "max_operator"
            ]
        else:
            item["max_operator"] = MAX_OPERATORS.getValue(max_op)
            item["min_operator"] = MIN_OPERATORS.getValue(min_op)
            item["allow_edit"] = []

        return item
