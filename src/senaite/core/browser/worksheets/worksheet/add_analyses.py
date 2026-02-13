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

from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import view
from plone.protect import CheckAuthenticator
from senaite.app.listing import ListingView

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PRIORITIES
from bika.lims.utils import get_display_list
from bika.lims.utils import get_image
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.i18n import translate
from senaite.core.i18n import translate as t
from senaite.core.permissions.worksheet import can_manage_worksheets


def getServiceUidsByMethod(method):
    if not api.is_uid(method):
        method = api.get_uid(method)

    query = {
        "portal_type": "AnalysisService",
        "is_active": True,
        "method_available_uid": method,
    }
    setup_catalog = api.get_tool(SETUP_CATALOG)
    uids = map(api.get_uid, setup_catalog(query))

    return uids


class AddAnalysesView(ListingView):
    """Assign Analyses View for Worksheets
    """
    template = ViewPageTemplateFile("templates/add_analyses.pt")

    def __init__(self, context, request):
        super(AddAnalysesView, self).__init__(context, request)

        self.catalog = ANALYSIS_CATALOG

        self.contentFilter = {
            "portal_type": "Analysis",
            "review_state": "unassigned",
            "sort_on": "getPrioritySortkey",
        }

        self.icon = api.get_icon("Worksheets", html_tag=False)

        self.title = translate(_(
            u"listing_add_analyses_title",
            default=u"Add Analyses"
        ))
        self.context_actions = {}

        # initial review state for first form display of the worksheet
        # add_analyses search view - first batch of analyses, latest first.

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.columns = collections.OrderedDict((
            ("Priority", {
                "title": "",
                "sortable": True,
                "index": "getPrioritySortkey"}),
            ("Client", {
                "title": _(
                    u"listing_add_analyses_column_client",
                    default=u"Client"
                ),
                "attr": "getClientTitle",
                "replace_url": "getClientURL",
                "index": "getClientTitle",
            }),
            ("getClientOrderNumber", {
                "title": _(
                    u"listing_add_analyses_column_client_order_number",
                    default=u"Order"
                ),
                "toggle": False,
                "attr": "getClientOrderNumber",
            }),
            ("getRequestID", {
                "title": _(
                    u"listing_add_analyses_column_request_id",
                    default=u"Request ID"
                ),
                "attr": "getRequestID",
                "replace_url": "getRequestURL",
                "index": "getRequestID",
            }),
            ("getCategoryTitle", {
                "title": _(
                    u"listing_add_analyses_column_category_title",
                    default=u"Category"
                ),
            }),
            ("Title", {
                "title": _(
                    u"listing_add_analyses_column_title",
                    default=u"Analysis"
                ),
                "index": "getId",
            }),
            ("getDateReceived", {
                "title": _(
                    u"listing_add_analyses_column_date_received",
                    default=u"Date Received"
                ),
                "index": "getDateReceived",
            }),
            ("getDueDate", {
                "title": _(
                    u"listing_add_analyses_column_due_date",
                    default=u"Due Date"
                ),
                "index": "getDueDate",
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_add_analyses_state_all",
                    default=u"All"
                ),
                "contentFilter": {},
                "transitions": [{"id": "assign"}, ],
                "columns": self.columns.keys(),
            },
        ]

    def __call__(self):
        super(AddAnalysesView, self).__call__()

        # Handle form submission
        if self.request.form.get("submitted"):
            CheckAuthenticator(self.request)
            success = self.handle_submit()
            if success:
                message = _(
                    u"changes_saved",
                    default=u"Changes saved."
                )
                self.add_status_message(message)
                ws_url = api.get_url(self.context)
                redirect_url = "{}/{}".format(ws_url, "manage_results")
                return self.request.response.redirect(redirect_url)

            message = _(
                u"no_analyses_added_to_this_worksheet",
                default=u"No analyses added to this worksheet."
            )
            self.add_status_message(message, "warning")
            return self.template()

        # handle subpath calls
        if len(self.traverse_subpath) > 0:
            return self.handle_subpath()

        return self.template()

    def update(self):
        """Update hook
        """
        super(AddAnalysesView, self).update()
        wst = self.context.getWorksheetTemplate()
        new_states = []
        if wst:

            wst_service_uids = wst.getRawServices()
            # restrict to the selected template services
            if wst_service_uids:
                new_states.append({
                    "id": "restrict_to_services",
                    "title": _(
                        u"listing_add_analyses_state_restrict_to_services",
                        default=u"Filter by template services"
                    ),
                    "contentFilter": {
                        "getServiceUID": wst_service_uids,
                    },
                    "transitions": [{"id": "assign"}, ],
                    "columns": self.columns.keys(),
                })
                self.default_review_state = "restrict_to_services"

            # restrict the available analysis services by method
            method = wst.getRawRestrictToMethod()
            if method:
                service_uids = getServiceUidsByMethod(method)
                new_states.append({
                    "id": "restrict_to_method",
                    "title": _(
                        u"listing_add_analyses_state_restrict_to_method",
                        default=u"Filter by template method"
                    ),
                    "contentFilter": {
                        "getServiceUID": service_uids
                    },
                    "transitions": [{"id": "assign"}, ],
                    "columns": self.columns.keys(),
                })
                self.default_review_state = "restrict_to_method"

        existing_state_ids = [rs.get("id") for rs in self.review_states]
        for new_state in new_states:
            if new_state.get("id") not in existing_state_ids:
                self.review_states.append(new_state)

    def handle_submit(self):
        """Handle form submission
        """
        wst_uid = self.request.form.get("getWorksheetTemplate")
        if not wst_uid:
            return False

        layout = self.context.getLayoutView()
        wst = api.get_object_by_uid(wst_uid)

        self.request["context_uid"] = api.get_uid(self.context)
        self.context.applyWorksheetTemplate(wst)

        if len(self.context.getLayoutView()) == len(layout):
            return False
        return True

    @property
    def worksheet_template_setup_url(self):
        """Returns the Worksheet Template Setup URL
        """
        setup = api.get_senaite_setup()
        return "{}/{}".format(api.get_url(setup), "worksheettemplates")

    @view.memoize
    def is_manage_allowed(self):
        """Check if manage is allowed
        """
        return can_manage_worksheets(self.context)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    @view.memoize
    def get_object_by_uid(self, uid):
        """Returns the object for the given uid or None
        """
        return api.get_object_by_uid(uid, default=None)

    def get_category_title(self, analysis):
        """Returns the title of the category the analysis is assigned to
        """
        obj = api.get_object(analysis)
        cat_uid = obj.getRawCategory()
        if not cat_uid:
            return ""
        cat = self.get_object_by_uid(cat_uid)
        return api.get_title(cat)

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """

        DueDate = obj.getDueDate

        item["getDateReceived"] = self.ulocalized_time(obj.getDateReceived)
        item["getDueDate"] = self.ulocalized_time(DueDate)

        if DueDate and DueDate < DateTime():
            item["after"]["DueDate"] = get_image(
                "late.png", title=t(_("Late Analysis")))

        # set category title
        item["getCategoryTitle"] = self.get_category_title(obj)

        # Add Priority column
        priority_sort_key = obj.getPrioritySortkey
        if not priority_sort_key:
            # Default priority is Medium = 3.
            # The format of PrioritySortKey is <priority>.<created>
            priority_sort_key = "3.%s" % obj.created.ISO8601()

        priority = priority_sort_key.split(".")[0]
        priority_text = t(PRIORITIES.getValue(priority))
        html = "<div title='{}' class='priority-ico priority-{}'><div>"
        item["replace"]["Priority"] = html.format(priority_text, priority)

        return item

    def getWorksheetTemplates(self):
        """Return WS Templates
        """
        query = {
            "portal_type": "WorksheetTemplate",
            "is_active": True,
            "sort_on": "sortable_title",
        }
        brains = api.search(query, SETUP_CATALOG)
        return get_display_list(brains)
