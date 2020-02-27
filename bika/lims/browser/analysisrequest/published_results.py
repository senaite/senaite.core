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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.browser.publish.reports_listing import ReportsListingView


class AnalysisRequestPublishedResults(ReportsListingView):
    """View of published results
    """

    def __init__(self, context, request):
        super(AnalysisRequestPublishedResults, self).__init__(context, request)

        # get the client for the catalog query
        client = context.getClient()
        client_path = api.get_path(client)

        # get the UID of the current context (sample)
        sample_uid = api.get_uid(context)

        self.contentFilter = {
            "portal_type": "ARReport",
            "path": {
                "query": client_path,
                "depth": 2,
            },
            # search all reports, where the current sample UID is included
            "sample_uid": [sample_uid],
            "sort_on": "created",
            "sort_order": "descending",
        }

        # disable the searchbox in this listing
        self.show_search = False

        # only allow the email transition at this level
        self.review_states = [
            {
                "id": "default",
                "title": "All",
                "contentFilter": {},
                "columns": self.columns.keys(),
                "custom_transitions": [
                    self.send_email_transition,
                ]
            },
        ]
