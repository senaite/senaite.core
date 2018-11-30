# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections
import json

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.permissions import EditWorksheet
from bika.lims.permissions import ManageWorksheets
from bika.lims.utils import get_display_list
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
        self.restrict_results = False
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
            ("Title", {
                "title": _("Worksheet"),
                "index": "getId"}),
            ("Analyst", {
                "title": _("Analyst"),
                "index": "getAnalyst"}),
            ("Template", {
                "title": _("Template"),
                "attr": "getWorksheetTemplateTitle",
                "replace_url": "getWorksheetTemplateURL"}),
            ("NumRegularSamples", {
                "title": _("Samples")}),
            ("NumQCAnalyses", {
                "title": _("QC Analyses")}),
            ("NumRegularAnalyses", {
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
                "title": _("All"),
                "contentFilter": {
                    "review_state": [
                        "open",
                        "to_be_verified",
                        "verified"
                    ],
                    "sort_on":"CreationDate",
                    "sort_order": "reverse"},
                "transitions":[
                    {"id": "retract"},
                    {"id": "verify"},
                    {"id": "reject"}
                ],
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
                "transitions":[
                    {"id": "retract"},
                    {"id": "verify"},
                    {"id": "reject"}
                ],
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
                "transitions": [
                    {"id": "retract"},
                    {"id": "verify"},
                    {"id": "reject"}
                ],
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

        roles = self.member.getRoles()
        self.restrict_results = "Manager" not in roles \
            and "LabManager" not in roles \
            and "LabClerk" not in roles \
            and "RegulatoryInspector" not in roles \
            and self.context.bika_setup.getRestrictWorksheetUsersAccess()

        if self.restrict_results:
            # Remove 'Mine' button and hide 'Analyst' column
            del self.review_states[1]  # Mine
            self.columns["Analyst"]["toggle"] = False

    def is_analyst_assignment_allowed(self):
        """Check if the analyst can be assigned
        """
        if not self.allow_edit:
            return False
        if not self.can_manage:
            return False
        if self.restrict_results:
            return False
        return True

    def allow_analyst_reassignment(self):
        """Allow the Analyst reassignment
        """
        reassing_analyst_transition = {
            "id": "reassign",
            "title": _("Reassign")}
        for rs in self.review_states:
            if rs["id"] not in ["default", "mine", "open"]:
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

    def folderitems(self):
        """Return folderitems as brains
        """
        return super(FolderView, self).folderitems(classic=False)

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """

        layout = obj.getLayout
        title = api.get_title(obj)
        url = api.get_url(obj)

        item["CreationDate"] = self.ulocalized_time(obj.created)
        if len(obj.getAnalysesUIDs) == 0:
            item["table_row_class"] = "state-empty-worksheet"

        title_link = "{}/{}".format(url, "add_analyses")
        if len(layout) > 0:
            title_link = "{}/{}".format(url, "manage_results")

        item["Title"] = title
        item["replace"]["Title"] = get_link(title_link, value=title)

        pos_parent = {}
        for slot in layout:
            # compensate for bad data caused by a stupid bug.
            if type(slot["position"]) in (list, tuple):
                slot["position"] = slot["position"][0]
            if slot["position"] == "new":
                continue
            if slot["position"] in pos_parent:
                continue
            pos_parent[slot["position"]] =\
                self.rc.lookupObject(slot.get("container_uid"))

        # Total QC Analyses
        item["NumQCAnalyses"] = str(obj.getNumberOfQCAnalyses)
        # Total Routine Analyses
        item["NumRegularAnalyses"] = str(obj.getNumberOfRegularAnalyses)
        # Total Number of Samples
        item["NumRegularSamples"] = str(obj.getNumberOfRegularSamples)

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
            "inactive_state": "active",
        }
        return api.search(query, "bika_setup_catalog")

    def _get_instruments_brains(self):
        """Returns all active Instruments

        :returns: list of brains
        """
        query = {
            "portal_type": "Instrument",
            "inactive_state": "active"
        }
        return api.search(query, "bika_setup_catalog")
