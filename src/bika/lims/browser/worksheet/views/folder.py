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
import json

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.permissions import EditWorksheet
from bika.lims.permissions import ManageWorksheets
from bika.lims.utils import get_display_list, get_progress_bar_html
from bika.lims.utils import get_link
from bika.lims.utils import getUsers
from bika.lims.utils import user_fullname
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class FolderView(BikaListingView):
    """Listing view for Worksheets
    """
    template = ViewPageTemplateFile("../templates/worksheets.pt")

    def __init__(self, context, request):
        super(FolderView, self).__init__(context, request)

        self.catalog = CATALOG_WORKSHEET_LISTING
        self.contentFilter = {
            "review_state": ["open", "to_be_verified", "verified", "rejected"],
            "sort_on": "created",
            "sort_order": "reverse"
        }

        self.title = self.context.translate(_("Worksheets"))
        self.description = ""

        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/worksheet_big.png"
        )

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=InstrumentMaintenanceTask",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.context_actions = {
            _("Add"): {
                "url": "worksheet_add",
                "icon": "++resource++bika.lims.images/add.png",
                "class": "worksheet_add"}
        }

        self.show_select_column = True
        self.show_select_all_checkbox = True
        self.filter_by_user = False
        self.selected_state = ""
        self.analyst_choices = []
        self.can_reassign = False
        self.can_manage = False

        self.rc = getToolByName(self, REFERENCE_CATALOG)

        # this is a property of self, because self.getAnalysts returns it
        self.analysts = getUsers(self, ["Manager", "LabManager", "Analyst"])
        self.analysts = self.analysts.sortedByValue()
        self.analyst_choices = []
        for a in self.analysts:
            self.analyst_choices.append({
                "ResultValue": a,
                "ResultText": self.analysts.getValue(a),
            })

        self.columns = collections.OrderedDict((
            ("getProgressPercentage", {
               "title": _("Progress")}),
            ("Title", {
                "title": _("Worksheet"),
                "index": "getId"}),
            ("Analyst", {
                "title": _("Analyst"),
                "index": "getAnalyst"}),
            ("getWorksheetTemplateTitle", {
                "title": _("Template"),
                "replace_url": "getWorksheetTemplateURL"}),
            ("getNumberOfRegularSamples", {
                "title": _("Samples")}),
            ("getNumberOfQCAnalyses", {
                "title": _("QC Analyses")}),
            ("getNumberOfRegularAnalyses", {
                "title": _("Routine Analyses")}),
            ("CreationDate", {
                "title": _("Created"),
                "index": "created"}),
            ("state_title", {
                "title": _("State"),
                "index": "review_state",
                "attr": "state_title"}),
        ))
        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {
                    "review_state": [
                        "open",
                        "to_be_verified",
                    ],
                    "sort_on": "CreationDate",
                    "sort_order": "reverse"},
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "open",
                "title": _("Open"),
                "contentFilter": {
                    "review_state": "open",
                    "sort_on": "CreationDate",
                    "sort_order": "reverse"},
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "to_be_verified",
                "title": _("To be verified"),
                "contentFilter": {
                    "review_state": "to_be_verified",
                    "sort_on": "CreationDate",
                    "sort_order": "reverse"},
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys()
            }, {
                "id": "verified",
                "title": _("Verified"),
                "contentFilter": {
                    "review_state": "verified",
                    "sort_on": "CreationDate",
                    "sort_order": "reverse"
                },
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {
                    "review_state": [
                        "open",
                        "to_be_verified",
                        "verified",
                        "rejected",
                    ],
                    "sort_on":"CreationDate",
                    "sort_order": "reverse"},
                "transitions":[],
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }, {
                # getAuthenticatedMember does not work in __init__ so "mine" is
                # configured further in "folderitems" below.
                "id": "mine",
                "title": _("Mine"),
                "contentFilter": {
                    "review_state": [
                        "open",
                        "to_be_verified",
                        "verified",
                        "rejected"
                    ],
                    "sort_on":"CreationDate",
                    "sort_order": "reverse"},
                "transitions":[],
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }
        ]

    def before_render(self):
        """Before render hook of the listing base view
        """
        super(FolderView, self).before_render()

        # disable the editable border of the Add-, Display- and Workflow menu
        self.request.set("disable_border", 1)

        # the current selected WF state
        self.selected_state = self.get_selected_state()

        self.allow_edit = self.is_edit_allowed()
        self.can_manage = self.is_manage_allowed()

        # Check if analysts can be assigned
        if self.is_analyst_assignment_allowed():
            self.can_reassign = True
            self.allow_analyst_reassignment()

        if not self.can_manage:
            # The current has no prvileges to manage WS.
            # Remove the add button
            self.context_actions = {}

        if self.context.bika_setup.getRestrictWorksheetUsersAccess():
            # Display only the worksheets assigned to the current user unless
            # the user belongs to a privileged role
            allowed = ["Manager", "LabManager", "RegulatoryInspector"]
            diff = filter(lambda role: role in allowed, self.member.getRoles())
            self.filter_by_user = len(diff) == 0

        if self.filter_by_user:
            # Remove 'Mine' button and hide 'Analyst' column
            del self.review_states[1]  # Mine
            self.columns["Analyst"]["toggle"] = False
            self.contentFilter["getAnalyst"] = self.member.id
            for rvw in self.review_states:
                rvw["contentFilter"]["getAnalyst"] = self.member.id

    def is_analyst_assignment_allowed(self):
        """Check if the analyst can be assigned
        """
        if not self.allow_edit:
            return False
        if not self.can_manage:
            return False
        if self.filter_by_user:
            return False
        return True

    def allow_analyst_reassignment(self):
        """Allow the Analyst reassignment
        """
        reassing_analyst_transition = {
            "id": "reassign",
            "title": _("Reassign")}
        for rs in self.review_states:
            if rs["id"] not in ["default", "mine", "open", "all"]:
                continue
            rs["custom_transitions"].append(reassing_analyst_transition)
        self.show_select_column = True
        self.show_workflow_action_buttons = True

    def is_manage_allowed(self):
        """Check if the User is allowed to manage
        """
        checkPermission = self.context.portal_membership.checkPermission
        return checkPermission(ManageWorksheets, self.context)

    def is_edit_allowed(self):
        """Check if edit is allowed
        """
        checkPermission = self.context.portal_membership.checkPermission
        return checkPermission(EditWorksheet, self.context)

    def get_selected_state(self):
        """Returns the current selected state
        """
        form_key = "{}_review_state".format(self.form_id)
        return self.request.get(form_key, "default")

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """

        title = api.get_title(obj)
        url = api.get_url(obj)

        item["CreationDate"] = self.ulocalized_time(obj.created)

        title_link = "{}/{}".format(url, "add_analyses")
        if len(obj.getAnalysesUIDs) > 0:
            title_link = "{}/{}".format(url, "manage_results")

        item["Title"] = title
        item["replace"]["Title"] = get_link(title_link, value=title)

        # Total QC Analyses
        item["getNumberOfQCAnalyses"] = str(
            obj.getNumberOfQCAnalyses)
        # Total Routine Analyses
        item["getNumberOfRegularAnalyses"] = str(
            obj.getNumberOfRegularAnalyses)
        # Total Number of Samples
        item["getNumberOfRegularSamples"] = str(
            obj.getNumberOfRegularSamples)

        # Progress
        progress = obj.getProgressPercentage
        progress_bar_html = get_progress_bar_html(progress)
        item["replace"]["getProgressPercentage"] = progress_bar_html

        review_state = item["review_state"]
        if self.can_reassign and review_state == "open":
            item["Analyst"] = obj.getAnalyst
            item["allow_edit"] = ["Analyst"]
            item["required"] = ["Analyst"]
            item["choices"] = {"Analyst": self.analyst_choices}
        else:
            fullname = user_fullname(self.context, obj.getAnalyst)
            item["Analyst"] = fullname

        return item

    def getAnalysts(self):
        """Returns all analysts
        """
        return self.analysts

    def getWorksheetTemplates(self):
        """Returns a DisplayList with all active worksheet templates

        :return: DisplayList of worksheet templates (uid, title)
        :rtype: DisplayList
        """
        brains = self._get_worksheet_templates_brains()
        return get_display_list(brains)

    def getInstruments(self):
        """Returns a DisplayList with all active Instruments

        :return: DisplayList of worksheet templates (uid, title)
        :rtype: DisplayList
        """
        brains = self._get_instruments_brains()
        return get_display_list(brains)

    def getTemplateInstruments(self):
        """Returns worksheet templates as JSON
        """
        items = dict()
        templates = self._get_worksheet_templates_brains()
        for template in templates:
            template_obj = api.get_object(template)
            uid_template = api.get_uid(template_obj)
            instrument = template_obj.getInstrument()
            uid_instrument = ""
            if instrument:
                uid_instrument = api.get_uid(instrument)
            items[uid_template] = uid_instrument

        return json.dumps(items)

    def _get_worksheet_templates_brains(self):
        """Returns all active worksheet templates

        :returns: list of worksheet template brains
        """
        query = {
            "portal_type": "WorksheetTemplate",
            "is_active": True,
        }
        return api.search(query, "bika_setup_catalog")

    def _get_instruments_brains(self):
        """Returns all active Instruments

        :returns: list of brains
        """
        query = {
            "portal_type": "Instrument",
            "is_active": True
        }
        return api.search(query, "bika_setup_catalog")
