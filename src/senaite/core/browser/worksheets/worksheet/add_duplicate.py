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
from operator import itemgetter

from plone.memoize import view
from plone.protect import CheckAuthenticator
from senaite.app.listing import ListingView

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import get_link
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.i18n import translate


class AddDuplicateView(ListingView):
    """Categorize Analyses by Slot/AR
    """

    def __init__(self, context, request):
        super(AddDuplicateView, self).__init__(context, request)

        self.catalog = ANALYSIS_CATALOG
        self.contentFilter = {
            "portal_type": "Analysis",
            "getWorksheetUID": "",
        }

        self.icon = api.get_icon("Worksheets", html_tag=False)

        self.context_actions = {}
        self.title = translate(_(
            u"listing_add_duplicate_title",
            default=u"Add Duplicate"
        ))

        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_column_toggles = False
        self.show_select_column = True
        self.pagesize = 999999
        self.allow_edit = True
        self.show_search = False
        self.show_categories = False

        self.columns = collections.OrderedDict((
            ("Position", {
                "title": _(
                    u"listing_add_duplication_column_title",
                    default=u"Position"
                ),
                "sortable": False,
            }),
            ("RequestID", {
                "title": _(
                    u"listing_add_duplication_column_request_id",
                    default=u"Request ID"
                ),
                "sortable": False,
            }),
            ("Client", {
                "title": _(
                    u"listing_add_duplication_column_client",
                    default=u"Client"
                ),
                "sortable": False,
            }),
            ("created", {
                "title": _(
                    u"listing_add_duplication_column_created",
                    default=u"Date Requested"
                ),
                "sortable": False,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_add_duplicate_state_all",
                    default=u"All"
                ),
                "contentFilter": {},
                "transitions": [{"id": "add"}],
                "custom_transitions": [
                    {
                        "id": "add",
                        "title": _("Add"),
                        "url": self.__name__,
                    }
                ],
                "columns": self.columns.keys()
            },
        ]

    def __call__(self):
        template = super(AddDuplicateView, self).__call__()

        # Handle form submission
        if self.request.form.get("submitted"):
            CheckAuthenticator(self.request)
            self.handle_submit()
        return template

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def handle_submit(self):
        """Handle form submission
        """
        form = self.request.form
        # Selected AR UIDs
        uids = form.get("uids")
        container_mapping = self.get_container_mapping()
        for uid in uids:
            src_pos = container_mapping[uid]
            self.context.addDuplicateAnalyses(src_pos)
        redirect_url = "{}/{}".format(
            api.get_url(self.context), "manage_results")
        self.request.response.redirect(redirect_url)

    @view.memoize
    def get_container_mapping(self):
        """Returns a mapping of container -> position
        """
        layout = self.context.getLayoutView()
        container_mapping = {}
        for slot in layout:
            if slot["type"] != "a":
                continue
            position = slot["position"]
            container_uid = slot["container_uid"]
            container_mapping[container_uid] = position
        return container_mapping

    def folderitems(self):
        """Custom folderitems for Worksheet ARs
        """
        items = []
        for ar, pos in self.get_container_mapping().items():
            ar = api.get_object_by_uid(ar)
            ar_id = api.get_id(ar)
            ar_uid = api.get_uid(ar)
            ar_url = api.get_url(ar)
            ar_title = api.get_title(ar)
            url = api.get_url(ar)
            client = ar.getClient()
            client_url = api.get_url(client)
            client_title = api.get_title(client)

            item = {
                "obj": ar,
                "id": ar_id,
                "uid": ar_uid,
                "title": ar_title,
                "type_class": "contenttype-AnalysisRequest",
                "url": url,
                "relative_url": url,
                "view_url": url,
                "Position": pos,
                "RequestID": ar_id,
                "Client": client_title,
                "created": self.ulocalized_time(ar.created(), long_format=1),
                "replace": {
                    "Client": get_link(client_url, value=client_title),
                    "RequestID": get_link(ar_url, value=ar_title),
                },
                "before": {},
                "after": {},
                "choices": {},
                "class": {},
                "state_class": "state-active",
                "allow_edit": [],
                "required": [],
            }
            items.append(item)
        items = sorted(items, key=itemgetter("Position"))
        return items
