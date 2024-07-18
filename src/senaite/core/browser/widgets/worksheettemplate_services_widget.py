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

import collections

from bika.lims import bikaMessageFactory as _
from plone.memoize import view

from .services_widget import ServicesWidget


class WorksheetTemplateServicesWidget(ServicesWidget):
    """Listing widget for Sample Template Services
    """

    def __init__(self, field, request):
        super(WorksheetTemplateServicesWidget, self).__init__(field, request)

        if self.context.getRestrictToMethod():
            method = self.context.getMethod()
            if method:
                self.contentFilter.update({
                    "method_available_uid": method.UID()
                })
        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _(
                    u"listing_services_column_title",
                    default=u"Service"
                ),
                "index": "sortable_title",
                "sortable": False
            }),
            ("Keyword", {
                "title": _(
                    u"listing_services_column_keyword",
                    default=u"Keyword"
                ),
                "sortable": False
            }),
            ("Methods", {
                "title": _(
                    u"listing_services_column_methods",
                    default=u"Methods"
                ),
                "sortable": False
            }),
            ("Calculation", {
                "title": _(
                    u"listing_services_column_calculation",
                    default=u"Calculation"
                ),
                "sortable": False
            }),
        ))

    @view.memoize
    def get_editable_columns(self):
        """Return editable fields
        """
        return []
