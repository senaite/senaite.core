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

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize
from senaite.core.browser.listing.base import ListingView

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import getUsers
from bika.lims.utils import get_display_list
from bika.lims.utils import get_link
from bika.lims.utils import get_progress_bar_html
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.catalog import WORKSHEET_CATALOG
from senaite.core.i18n import translate
from senaite.core.permissions import AddWorksheet
from senaite.core.permissions.worksheet import can_add_worksheet
from senaite.core.permissions.worksheet import can_edit_worksheet
from senaite.core.permissions.worksheet import can_manage_worksheets


class WorksheetsView(ListingView):
    """Listing View for Worksheets
    """
    template = ViewPageTemplateFile("templates/view.pt")

    # Open the worksheet manage view instead of the generic /edit form.
    # No URL suffix needed — the manage view is the default view.
    edit_view = "manage_results"

    def __init__(self, context, request):
        super(WorksheetsView, self).__init__(context, request)

        self.catalog = WORKSHEET_CATALOG

        self.contentFilter = {
            "review_state": ["open", "to_be_verified", "verified", "rejected"],
            "sort_on": "created",
            "sort_order": "reverse"
        }

        self.context_actions = {
            _(u"listing_worksheets_action_add", default=u"Add"): {
                "url": "add_worksheet",
                "icon": "++resource++bika.lims.images/add.png",
                "class": "worksheet_add",
                "permission": AddWorksheet,
            }
        }

        self.title = translate(_(
            u"listing_worksheets_title",
            default=u"Worksheets"
        ))
        self.description = ""
        self.icon = api.get_icon("Worksheets", html_tag=False)
        self.show_select_column = True
        self.show_select_all_checkbox = True

        self.selected_state = "default"
        self.allow_edit = False
        self.can_manage = False
        self.can_reassign = False
        self.show_workflow_action_buttons = False
        self.analyst_choices = []
        self.can_reassign = False
        self.can_manage = False

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
                "title": _(
                    u"listing_worksheets_column_progress",
                    default=u"Progress"
                ),
            }),
            ("Title", {
                "title": _(
                    u"listing_worksheets_column_title",
                    default=u"Worksheet"
                ),
                "index": "getId",
            }),
            ("Analyst", {
                "title": _(
                    u"listing_worksheets_column_analyst",
                    default=u"Analyst"
                ),
                "index": "getAnalyst",
            }),
            ("getWorksheetTemplateTitle", {
                "title": _(
                    u"listing_worksheets_column_template_title",
                    default=u"Template"
                ),
                "replace_url": "getWorksheetTemplateURL",
            }),
            ("getNumberOfRegularSamples", {
                "title": _(
                    u"listing_worksheets_column_number_samples",
                    default=u"Samples"
                ),
            }),
            ("getNumberOfQCAnalyses", {
                "title": _(
                    u"listing_worksheets_column_number_qc_analyses",
                    default=u"QC Analyses"
                ),
            }),
            ("getNumberOfRegularAnalyses", {
                "title": _(
                    u"listing_worksheets_column_number_analyses",
                    default=u"Routine Analyses"
                ),
            }),
            ("CreationDate", {
                "title": _(
                    u"listing_worksheets_column_created",
                    default=u"Created"
                ),
                "index": "created",
            }),
            ("state_title", {
                "title": _(
                    u"listing_worksheets_column_state_title",
                    default=u"State"
                ),
                "index": "review_state",
                "attr": "state_title",
            }),
        ))
        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_worksheets_state_active",
                    default=u"Active"
                ),
                "contentFilter": {
                    "review_state": [
                        "open",
                        "to_be_verified",
                    ],
                    "sort_on": "created",
                    "sort_order": "reverse",
                },
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "open",
                "title": _(
                    u"listing_worksheets_state_open",
                    default=u"Open"
                ),
                "contentFilter": {
                    "review_state": "open",
                    "sort_on": "created",
                    "sort_order": "reverse",
                },
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "to_be_verified",
                "title": _(
                    u"listing_worksheets_state_to_be_verified",
                    default=u"To be verified"
                ),
                "contentFilter": {
                    "review_state": "to_be_verified",
                    "sort_on": "created",
                    "sort_order": "reverse",
                },
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys()
            }, {
                "id": "verified",
                "title": _(
                    u"listing_worksheets_state_verified",
                    default=u"Verified"
                ),
                "contentFilter": {
                    "review_state": "verified",
                    "sort_on": "created",
                    "sort_order": "reverse"
                },
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    u"listing_worksheets_state_all",
                    default=u"All"
                ),
                "contentFilter": {
                    "review_state": [
                        "open",
                        "to_be_verified",
                        "verified",
                        "rejected",
                    ],
                    "sort_on": "created",
                    "sort_order": "reverse",
                },
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }, {
                # getAuthenticatedMember does not work in __init__ so "mine" is
                # configured further in "folderitems" below.
                "id": "mine",
                "title": _(
                    u"listing_worksheets_state_mine",
                    default=u"Mine"
                ),
                "contentFilter": {
                    "review_state": [
                        "open",
                        "to_be_verified",
                        "verified",
                        "rejected"
                    ],
                    "sort_on": "created",
                    "sort_order": "reverse",
                },
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }
        ]

    def before_render(self):
        """Before render hook of the listing base view
        """
        super(WorksheetsView, self).before_render()

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

        # Update the "Mine" review status with current user id
        mine = self.get_review_state("mine")
        mine["contentFilter"]["getAnalyst"] = self.member.id

        if self.show_only_mine():
            # Remove 'Mine' button and hide 'Analyst' column
            self.remove_review_state("mine")
            self.columns["Analyst"]["toggle"] = False
            self.contentFilter["getAnalyst"] = self.member.id
            for rvw in self.review_states:
                rvw["contentFilter"]["getAnalyst"] = self.member.id

    def remove_review_state(self, id):
        """Removes the review status button with the given id
        """
        ids = [review_state["id"] for review_state in self.review_states]
        if id not in ids:
            return
        index = ids.index(id)
        del self.review_states[index]

    def is_privileged_user(self):
        """Returns whether the current user is a privileged member
        """
        privileged = ["Manager", "LabManager", "RegulatoryInspector"]
        user_roles = self.member.getRoles()
        if set(privileged).intersection(user_roles):
            return True
        return False

    @memoize
    def show_only_mine(self):
        """Returns whether only the worksheets assigned to current user have
        to be displayed or not
        """
        # do not filter if user is a privileged member
        if self.is_privileged_user():
            return False
        return api.get_senaite_setup().getRestrictWorksheetUsersAccess()

    def is_analyst_assignment_allowed(self):
        """Check if the analyst can be assigned
        """
        if not self.allow_edit:
            return False
        if not self.can_manage:
            return False
        if self.show_only_mine():
            return False
        return True

    def allow_analyst_reassignment(self):
        """Allow the Analyst reassignment
        """
        reassing_analyst_transition = {
            "id": "reassign",
            "title": _("Reassign"),
        }
        for rs in self.review_states:
            if rs["id"] not in ["default", "mine", "open", "all"]:
                continue
            rs["custom_transitions"].append(reassing_analyst_transition)
        self.show_select_column = True
        self.show_workflow_action_buttons = True

    def can_add(self):
        """Check if the user is allowed to add a worksheet
        """
        return can_add_worksheet(self.context)

    def is_manage_allowed(self):
        """Check if the User is allowed to manage
        """
        return can_manage_worksheets(self.context)

    def is_edit_allowed(self):
        """Check if edit is allowed
        """
        return can_edit_worksheet(self.context)

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

        url = api.get_url(obj)
        title = api.get_title(obj)
        if not title:
            title = api.get_object(obj).Title()

        item["Title"] = title
        item["replace"]["Title"] = get_link(url, value=title)

        item["CreationDate"] = self.ulocalized_time(obj.created)

        # Total QC Analyses
        item["getNumberOfQCAnalyses"] = str(obj.getNumberOfQCAnalyses)
        # Total Routine Analyses
        item["getNumberOfRegularAnalyses"] = str(
            obj.getNumberOfRegularAnalyses)
        # Total Number of Samples
        item["getNumberOfRegularSamples"] = str(obj.getNumberOfRegularSamples)

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
            fullname = self.user_fullname(obj.getAnalyst)
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

    def _get_worksheet_templates_brains(self):
        """Returns all active worksheet templates

        :returns: list of worksheet template brains
        """
        query = {
            "portal_type": "WorksheetTemplate",
            "is_active": True,
            "sort_on": "sortable_title",
        }
        return api.search(query, SETUP_CATALOG)

    def _get_instruments_brains(self):
        """Returns all active Instruments

        :returns: list of brains
        """
        query = {
            "portal_type": "Instrument",
            "is_active": True,
            "sort_on": "sortable_title",
        }
        return api.search(query, SETUP_CATALOG)
