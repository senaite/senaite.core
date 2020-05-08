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

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.worksheet.tools import showRejectionMessage
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import PRIORITIES
from bika.lims.permissions import EditWorksheet
from bika.lims.permissions import ManageWorksheets
from bika.lims.utils import get_image
from bika.lims.utils import t
from bika.lims.vocabularies import CatalogVocabulary
from DateTime import DateTime
from plone.memoize import view
from plone.protect import CheckAuthenticator
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AddAnalysesView(BikaListingView):
    """Assign Analyses View for Worksheets
    """
    template = ViewPageTemplateFile("../templates/add_analyses.pt")

    def __init__(self, context, request):
        super(AddAnalysesView, self).__init__(context, request)

        self.catalog = CATALOG_ANALYSIS_LISTING

        self.contentFilter = {
            "portal_type": "Analysis",
            "review_state": "unassigned",
            "isSampleReceived": True,
            "sort_on": "getPrioritySortkey",
        }

        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/worksheet_big.png"
        )

        self.title = self.context.translate(_("Add Analyses"))
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
                "title": _("Client"),
                "attr": "getClientTitle",
                "replace_url": "getClientURL",
                "index": "getClientTitle"}),
            ("getClientOrderNumber", {
                "title": _("Order"),
                "toggle": False,
                "attr": "getClientOrderNumber"}),
            ("getRequestID", {
                "title": _("Request ID"),
                "attr": "getRequestID",
                "replace_url": "getRequestURL",
                "index": "getRequestID"}),
            ("getCategoryTitle", {
                "title": _("Category"),
                "attr": "getCategoryTitle"}),
            ("Title", {
                "title": _("Analysis"),
                "index": "getId"}),
            ("getDateReceived", {
                "title": _("Date Received"),
                "index": "getDateReceived"}),
            ("getDueDate", {
                "title": _("Due Date"),
                "index": "getDueDate"}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "transitions": [{"id": "assign"}, ],
                "columns": self.columns.keys(),
            },
        ]

    def __call__(self):
        super(AddAnalysesView, self).__call__()

        # TODO: Refactor Worfklow
        grant = self.is_edit_allowed() and self.is_manage_allowed()
        if not grant:
            redirect_url = api.get_url(self.context)
            return self.request.response.redirect(redirect_url)

        # TODO: Refactor this function call
        showRejectionMessage(self.context)

        # Handle form submission
        if self.request.form.get("submitted"):
            CheckAuthenticator(self.request)
            success = self.handle_submit()
            if success:
                self.add_status_message(_("Changes saved."))
                redirect_url = "{}/{}".format(
                    api.get_url(self.context), "manage_results")
                self.request.response.redirect(redirect_url)
            else:
                self.add_status_message(
                    _("No analyses were added to this worksheet."),
                    level="warning")
            return self.template()

        # handle subpath calls
        if len(self.traverse_subpath) > 0:
            return self.handle_subpath()

        return self.template()

    def update(self):
        """Update hook
        """
        super(AddAnalysesView, self).update()

    def handle_submit(self):
        """Handle form submission
        """
        wst_uid = self.request.form.get("getWorksheetTemplate")
        if not wst_uid:
            return False

        layout = self.context.getLayout()
        wst = api.get_object_by_uid(wst_uid)

        self.request["context_uid"] = api.get_uid(self.context)
        self.context.applyWorksheetTemplate(wst)

        if len(self.context.getLayout()) == len(layout):
            return False
        return True

    @property
    def worksheet_template_setup_url(self):
        """Returns the Worksheet Template Setup URL
        """
        setup = api.get_setup()
        return "{}/{}".format(api.get_url(setup), "bika_worksheettemplates")

    @view.memoize
    def is_edit_allowed(self):
        """Check if edit is allowed
        """
        checkPermission = self.context.portal_membership.checkPermission
        return checkPermission(EditWorksheet, self.context)

    @view.memoize
    def is_manage_allowed(self):
        """Check if manage is allowed
        """
        checkPermission = self.context.portal_membership.checkPermission
        return checkPermission(ManageWorksheets, self.context)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

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
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = "bika_setup_catalog"
        return vocabulary(
            portal_type="WorksheetTemplate", sort_on="sortable_title")
