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
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.permissions import EditWorksheet
from bika.lims.permissions import ManageWorksheets
from bika.lims.utils import get_link
from plone.memoize import view
from plone.protect import CheckAuthenticator


class ReferenceSamplesView(BikaListingView):
    """Displays reference control samples
    """

    def __init__(self, context, request):
        super(ReferenceSamplesView, self).__init__(context, request)

        self.catalog = "bika_catalog"
        self.contentFilter = {
            "portal_type": "ReferenceSample",
            "getSupportedServices": self.get_assigned_services_uids(),
            "isValid": True,
            "review_state": "current",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {}
        self.title = _("Add Control Reference")

        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_column_toggles = False
        self.show_select_column = True
        self.show_categories = False
        self.pagesize = 999999
        self.allow_edit = True
        self.show_search = False

        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/worksheet_big.png"
        )

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Reference Sample"),
                "sortable": False}),
            ("SupportedServices", {
                "title": _("Supported Services"),
                "type": "multiselect",
                "sortable": False}),
            ("Position", {
                "title": _("Position"),
                "sortable": False}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
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
        template = super(ReferenceSamplesView, self).__call__()
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
            self.handle_submit()
        return template

    def update(self):
        """Update hook
        """
        super(ReferenceSamplesView, self).update()

    def handle_submit(self):
        """Handle form submission
        """
        form = self.request.form
        # Selected service UIDs
        uids = form.get("uids")
        # reference sample -> selected services mapping
        supported_services = form.get("SupportedServices")
        # service -> position mapping
        positions = form.get("Position")[0]
        for uid in uids:
            position = positions.get(uid)
            if position == "new":
                position = None
            service_uids = supported_services.get(uid)
            referencesample = api.get_object_by_uid(uid)
            self.context.addReferenceAnalyses(
                referencesample, service_uids, slot=position)
        redirect_url = "{}/{}".format(
            api.get_url(self.context), "manage_results")
        self.request.response.redirect(redirect_url)

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

    @view.memoize
    def get_editable_columns(self):
        """Return editable fields
        """
        columns = ["Position", "SupportedServices"]
        return columns

    @view.memoize
    def get_assigned_services(self):
        """Get the current assigned services of this Worksheet
        """
        analyses = self.context.getAnalyses()
        routine_analyses = filter(
            lambda an: IRoutineAnalysis.providedBy(an), analyses)
        services = map(lambda an: an.getAnalysisService(), routine_analyses)
        return services

    @view.memoize
    def get_assigned_services_uids(self):
        """Get the current assigned services UIDs of this Worksheet
        """
        services = self.get_assigned_services()
        uids = map(api.get_uid, services)
        return list(set(uids))

    def get_supported_services_uids(self, referencesample):
        """Get the supported services of the reference sample
        """
        uids = referencesample.getSupportedServices(only_uids=True)
        return list(set(uids))

    def make_supported_services_choices(self, referencesample):
        """Create choices for supported services
        """
        choices = []
        assigned_services = self.get_assigned_services_uids()
        for uid in self.get_supported_services_uids(referencesample):
            service = api.get_object(uid)
            title = api.get_title(service)
            selected = uid in assigned_services
            choices.append({
                "ResultValue": uid,
                "ResultText": title,
                "selected": selected,
            })
        return choices

    @view.memoize
    def make_position_choices(self):
        """Create choices for available positions
        """
        choices = []
        for pos in self.get_available_positions():
            choices.append({
                "ResultValue": pos,
                "ResultText": pos,
            })
        return choices

    @view.memoize
    def get_available_positions(self):
        """Return a list of empty slot numbers
        """
        available_positions = ["new"]
        layout = self.context.getLayout()
        used_positions = [int(slot["position"]) for slot in layout]
        if used_positions:
            used = [
                pos for pos in range(1, max(used_positions) + 1) if
                pos not in used_positions]
            available_positions.extend(used)
        return available_positions

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        item = super(ReferenceSamplesView, self).folderitem(obj, item, index)

        # ensure we have an object and not a brain
        obj = api.get_object(obj)
        url = api.get_url(obj)
        title = api.get_title(obj)

        item["Title"] = title
        item["replace"]["Title"] = get_link(url, value=title)
        item["allow_edit"] = self.get_editable_columns()

        # Supported Services
        supported_services_choices = self.make_supported_services_choices(obj)
        item["choices"]["SupportedServices"] = supported_services_choices

        # Position
        item["Position"] = "new"
        item["choices"]["Position"] = self.make_position_choices()

        return item
