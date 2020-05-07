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

from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import PRIORITIES
from bika.lims.permissions import AddAnalysisRequest
from bika.lims.permissions import TransitionSampleSample
from bika.lims.utils import getUsers
from bika.lims.utils import get_image
from bika.lims.utils import get_progress_bar_html
from bika.lims.utils import t


class AnalysisRequestsView(BikaListingView):
    """Listing View for all Analysis Requests in the System
    """

    template = ViewPageTemplateFile("templates/analysisrequests.pt")

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)

        # hide the right column
        request.set("disable_plone.rightcolumn", 1)

        # hide the editable border
        if self.context.portal_type == "AnalysisRequestsFolder":
            self.request.set("disable_border", 1)

        # catalog used for the query
        self.catalog = CATALOG_ANALYSIS_REQUEST_LISTING

        self.contentFilter = {
            "sort_on": "created",
            "sort_order": "descending",
            "isRootAncestor": True,  # only root ancestors
        }

        self.context_actions = {}

        self.allow_edit = True

        self.show_select_row = False
        self.show_select_column = True
        self.form_id = "analysisrequests"

        ar_image_path = "/++resource++bika.lims.images/sample_big.png"
        self.icon = "{}{}".format(self.portal_url, ar_image_path)
        self.title = self.context.translate(_("Samples"))
        self.description = ""

        SamplingWorkflowEnabled = \
            self.context.bika_setup.getSamplingWorkflowEnabled()

        self.columns = collections.OrderedDict((
            ("Priority", {
                "title": "",
                "index": "getPrioritySortkey",
                "sortable": True, }),
            ("Progress", {
                "title": "Progress",
                "index": "getProgress",
                "sortable": True,
                "toggle": True}),
            ("getId", {
                "title": _("Sample ID"),
                "attr": "getId",
                "replace_url": "getURL",
                "index": "getId"}),
            ("getClientOrderNumber", {
                "title": _("Client Order"),
                "sortable": True,
                "toggle": False}),
            ("Creator", {
                "title": _("Creator"),
                "index": "getCreatorFullName",
                "sortable": True,
                "toggle": True}),
            ("Created", {
                "title": _("Date Registered"),
                "index": "created",
                "toggle": False}),
            ("SamplingDate", {
                "title": _("Expected Sampling Date"),
                "index": "getSamplingDate",
                "toggle": SamplingWorkflowEnabled}),
            ("getDateSampled", {
                "title": _("Date Sampled"),
                "toggle": True,
                "input_class": "datetimepicker_nofuture",
                "input_width": "10"}),
            ("getDatePreserved", {
                "title": _("Date Preserved"),
                "toggle": False,
                "input_class": "datetimepicker_nofuture",
                "input_width": "10",
                "sortable": False}),  # no datesort without index
            ("getDateReceived", {
                "title": _("Date Received"),
                "toggle": False}),
            ("getDueDate", {
                "title": _("Due Date"),
                "toggle": False}),
            ("getDateVerified", {
                "title": _("Date Verified"),
                "input_width": "10",
                "toggle": False}),
            ("getDatePublished", {
                "title": _("Date Published"),
                "toggle": False}),
            ("BatchID", {
                "title": _("Batch ID"),
                "index": "getBatchID",
                "sortable": True,
                "toggle": False}),
            ("Client", {
                "title": _("Client"),
                "index": "getClientTitle",
                "attr": "getClientTitle",
                "replace_url": "getClientURL",
                "toggle": True}),
            ("ClientID", {
                "title": _("Client ID"),
                "index": "getClientID",
                "attr": "getClientID",
                "replace_url": "getClientURL",
                "toggle": True}),
            ("Province", {
                "title": _("Province"),
                "sortable": True,
                "index": "getProvince",
                "attr": "getProvince",
                "toggle": False}),
            ("District", {
                "title": _("District"),
                "sortable": True,
                "index": "getDistrict",
                "attr": "getDistrict",
                "toggle": False}),
            ("getClientReference", {
                "title": _("Client Ref"),
                "sortable": True,
                "index": "getClientReference",
                "toggle": False}),
            ("getClientSampleID", {
                "title": _("Client SID"),
                "toggle": False}),
            ("ClientContact", {
                "title": _("Contact"),
                "sortable": True,
                "index": "getContactFullName",
                "toggle": False}),
            ("getSampleTypeTitle", {
                "title": _("Sample Type"),
                "sortable": True,
                "toggle": True}),
            ("getSamplePointTitle", {
                "title": _("Sample Point"),
                "sortable": True,
                "index": "getSamplePointTitle",
                "toggle": False}),
            ("getStorageLocation", {
                "title": _("Storage Location"),
                "sortable": True,
                "index": "getStorageLocationTitle",
                "toggle": False}),
            ("SamplingDeviation", {
                "title": _("Sampling Deviation"),
                "sortable": True,
                "index": "getSamplingDeviationTitle",
                "toggle": False}),
            ("getSampler", {
                "title": _("Sampler"),
                "toggle": SamplingWorkflowEnabled}),
            ("getPreserver", {
                "title": _("Preserver"),
                "sortable": False,
                "toggle": False}),
            ("getProfilesTitle", {
                "title": _("Profile"),
                "sortable": True,
                "index": "getProfilesTitle",
                "toggle": False}),
            ("getAnalysesNum", {
                "title": _("Number of Analyses"),
                "sortable": True,
                "index": "getAnalysesNum",
                "toggle": False}),
            ("getTemplateTitle", {
                "title": _("Template"),
                "sortable": True,
                "index": "getTemplateTitle",
                "toggle": False}),
            ("Printed", {
                "title": _("Printed"),
                "sortable": False,
                "index": "getPrinted",
                "toggle": False}),
            ("state_title", {
                "title": _("State"),
                "sortable": True,
                "index": "review_state"}),
        ))

        # custom print transition
        print_stickers = {
            "id": "print_stickers",
            "title": _("Print stickers"),
            "url": "workflow_action?action=print_stickers"
        }

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {
                    "review_state": (
                        "sample_registered",
                        "scheduled_sampling",
                        "to_be_sampled",
                        "sample_due",
                        "sample_received",
                        "attachment_due",
                        "to_be_preserved",
                        "to_be_verified",
                        "verified",
                    ),
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }, {
                "id": "to_be_sampled",
                "title": _("To Be Sampled"),
                "contentFilter": {
                    "review_state": ("to_be_sampled",),
                    "sort_on": "created",
                    "sort_order": "descending"},
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys()
            }, {
                "id": "to_be_preserved",
                "title": _("To Be Preserved"),
                "contentFilter": {
                    "review_state": ("to_be_preserved",),
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }, {
                "id": "scheduled_sampling",
                "title": _("Scheduled sampling"),
                "contentFilter": {
                    "review_state": ("scheduled_sampling",),
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }, {
                "id": "sample_due",
                "title": _("Due"),
                "contentFilter": {
                    "review_state": (
                        "to_be_sampled",
                        "to_be_preserved",
                        "sample_due"),
                    "sort_on": "created",
                    "sort_order": "descending"},
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }, {
                "id": "sample_received",
                "title": _("Received"),
                "contentFilter": {
                    "review_state": "sample_received",
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }, {
                "id": "to_be_verified",
                "title": _("To be verified"),
                "contentFilter": {
                    "review_state": "to_be_verified",
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }, {
                "id": "verified",
                "title": _("Verified"),
                "contentFilter": {
                    "review_state": "verified",
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }, {
                "id": "published",
                "title": _("Published"),
                "contentFilter": {
                    "review_state": ("published"),
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "cancelled",
                "title": _("Cancelled"),
                "contentFilter": {
                    "review_state": "cancelled",
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "invalid",
                "title": _("Invalid"),
                "contentFilter": {
                    "review_state": "invalid",
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }, {
                "id": "rejected",
                "title": _("Rejected"),
                "contentFilter": {
                    "review_state": "rejected",
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [
                    {
                        "id": "print_stickers",
                        "title": _("Print stickers"),
                        "url": "workflow_action?action=print_stickers"},
                ],
                "columns": self.columns.keys(),
            }, {
                "id": "assigned",
                "title": get_image("assigned.png",
                                   title=t(_("Assigned"))),
                "contentFilter": {
                    "assigned_state": "assigned",
                    "review_state": ("sample_received",
                                     "attachment_due",),
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }, {
                "id": "unassigned",
                "title": get_image("unassigned.png",
                                   title=t(_("Unsassigned"))),
                "contentFilter": {
                    "assigned_state": "unassigned",
                    "review_state": (
                        "sample_received",
                        "attachment_due",
                    ),
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }, {
                "id": "late",
                "title": get_image("late.png",
                                   title=t(_("Late"))),
                "contentFilter": {
                    # Query only for unpublished ARs that are late
                    "review_state": (
                        "sample_received",
                        "attachment_due",
                        "to_be_verified",
                        "verified",
                    ),
                    "getDueDate": {
                        "query": DateTime(),
                        "range": "max",
                    },
                    "sort_on": "created",
                    "sort_order": "descending",
                },
                "custom_transitions": [print_stickers],
                "columns": self.columns.keys(),
            }
        ]

    def update(self):
        """Called before the listing renders
        """
        super(AnalysisRequestsView, self).update()

        self.workflow = api.get_tool("portal_workflow")
        self.member = self.mtool.getAuthenticatedMember()
        self.roles = self.member.getRoles()

        setup = api.get_bika_setup()

        # remove `to_be_sampled` filter
        if not setup.getSamplingWorkflowEnabled():
            self.review_states = filter(
                lambda x: x.get("id") != "to_be_sampled", self.review_states)

        # remove `scheduled_sampling` filter
        if not setup.getScheduleSamplingEnabled():
            self.review_states = filter(
                lambda x: x.get("id") != "scheduled_sampling",
                self.review_states)

        # remove `to_be_preserved` filter
        if not setup.getSamplePreservationEnabled():
            self.review_states = filter(
                lambda x: x.get("id") != "to_be_preserved", self.review_states)

        # remove `rejected` filter
        if not setup.getRejectionReasons():
            self.review_states = filter(
                lambda x: x.get("id") != "rejected", self.review_states)

        self.hideclientlink = "RegulatoryInspector" in self.roles \
            and "Manager" not in self.roles \
            and "LabManager" not in self.roles \
            and "LabClerk" not in self.roles

        if self.context.portal_type == "AnalysisRequestsFolder" and \
                (self.mtool.checkPermission(AddAnalysisRequest, self.context)):
            self.context_actions[_("Add")] = \
                {"url": "ar_add?ar_count=1",
                 'permission': 'Add portal content',
                 "icon": "++resource++bika.lims.images/add.png"}

        self.editresults = -1
        self.clients = {}
        # self.user_is_preserver = "Preserver" in self.roles
        # Printing workflow enabled?
        # If not, remove the Column
        self.printwfenabled = \
            self.context.bika_setup.getPrintingWorkflowEnabled()
        printed_colname = "Printed"
        if not self.printwfenabled and printed_colname in self.columns:
            # Remove "Printed" columns
            del self.columns[printed_colname]
            tmprvs = []
            for rs in self.review_states:
                tmprs = rs
                tmprs["columns"] = [c for c in rs.get("columns", []) if
                                    c != printed_colname]
                tmprvs.append(tmprs)
            self.review_states = tmprvs
        elif self.printwfenabled:
            # Print button to choose multiple ARs and print them.
            review_states = []
            for review_state in self.review_states:
                review_state.get("custom_transitions", []).extend(
                    [{"id": "print_sample",
                      "title": _("Print"),
                      "url": "workflow_action?action=print_sample"}, ])
                review_states.append(review_state)
            self.review_states = review_states

        # Only "senaite.core: ManageAnalysisRequests" may see the copy to new button.
        # elsewhere it is hacked in where required.
        if self.copy_to_new_allowed:
            review_states = []
            for review_state in self.review_states:
                review_state.get("custom_transitions", []).extend(
                    [{"id": "copy_to_new",
                      "title": _("Copy to new"),
                      "url": "workflow_action?action=copy_to_new"}, ])
                review_states.append(review_state)
            self.review_states = review_states

    def before_render(self):
        """Before template render hook
        """
        # If the current user is a client contact, display those analysis
        # requests that belong to same client only
        super(AnalysisRequestsView, self).before_render()
        client = api.get_current_client()
        if client:
            self.contentFilter['path'] = {
                "query": "/".join(client.getPhysicalPath()),
                "level": 0}
            # No need to display the Client column
            self.remove_column('Client')

    def folderitem(self, obj, item, index):
        # Additional info from AnalysisRequest to be added in the item
        # generated by default by bikalisting.
        # Call the folderitem method from the base class
        item = BikaListingView.folderitem(self, obj, item, index)
        if not item:
            return None

        item["Creator"] = self.user_fullname(obj.Creator)
        # If we redirect from the folderitems view we should check if the
        # user has permissions to medify the element or not.
        priority_sort_key = obj.getPrioritySortkey
        if not priority_sort_key:
            # Default priority is Medium = 3.
            # The format of PrioritySortKey is <priority>.<created>
            priority_sort_key = "3.%s" % obj.created.ISO8601()
        priority = priority_sort_key.split(".")[0]
        priority_text = PRIORITIES.getValue(priority)
        priority_div = """<div class="priority-ico priority-%s">
                          <span class="notext">%s</span><div>
                       """
        item["replace"]["Priority"] = priority_div % (priority, priority_text)
        item["replace"]["getProfilesTitle"] = obj.getProfilesTitleStr

        analysesnum = obj.getAnalysesNum
        if analysesnum:
            num_verified = str(analysesnum[0])
            num_total = str(analysesnum[1])
            item["getAnalysesNum"] = "{0}/{1}".format(num_verified, num_total)
        else:
            item["getAnalysesNum"] = ""

        # Progress
        progress_perc = obj.getProgress
        item["Progress"] = progress_perc
        item["replace"]["Progress"] = get_progress_bar_html(progress_perc)

        item["BatchID"] = obj.getBatchID
        if obj.getBatchID:
            item['replace']['BatchID'] = "<a href='%s'>%s</a>" % \
                (obj.getBatchURL, obj.getBatchID)
        # TODO: SubGroup ???
        # val = obj.Schema().getField('SubGroup').get(obj)
        # item['SubGroup'] = val.Title() if val else ''

        date = obj.getSamplingDate
        item["SamplingDate"] = \
            self.ulocalized_time(date, long_format=1) if date else ""
        date = obj.getDateReceived
        item["getDateReceived"] = \
            self.ulocalized_time(date, long_format=1) if date else ""
        date = obj.getDueDate
        item["getDueDate"] = \
            self.ulocalized_time(date, long_format=1) if date else ""
        date = obj.getDatePublished
        item["getDatePublished"] = \
            self.ulocalized_time(date, long_format=1) if date else ""
        date = obj.getDateVerified
        item["getDateVerified"] = \
            self.ulocalized_time(date, long_format=1) if date else ""

        if self.printwfenabled:
            item["Printed"] = ""
            printed = obj.getPrinted if hasattr(obj, "getPrinted") else "0"
            print_icon = ""
            if printed == "0":
                print_icon = get_image("delete.png",
                                       title=t(_("Not printed yet")))
            elif printed == "1":
                print_icon = get_image("ok.png",
                                       title=t(_("Printed")))
            elif printed == "2":
                print_icon = get_image(
                    "exclamation.png",
                    title=t(_("Republished after last print")))
            item["after"]["Printed"] = print_icon
        item["SamplingDeviation"] = obj.getSamplingDeviationTitle

        item["getStorageLocation"] = obj.getStorageLocationTitle

        after_icons = ""
        if obj.assigned_state == 'assigned':
            after_icons += get_image("worksheet.png",
                                     title=t(_("All analyses assigned")))
        if item["review_state"] == 'invalid':
            after_icons += get_image("delete.png",
                                     title=t(_("Results have been withdrawn")))

        due_date = obj.getDueDate
        if due_date and due_date < (obj.getDatePublished or DateTime()):
            due_date_str = self.ulocalized_time(due_date)
            img_title = "{}: {}".format(t(_("Late Analyses")), due_date_str)
            after_icons += get_image("late.png", title=img_title)

        if obj.getSamplingDate and obj.getSamplingDate > DateTime():
            after_icons += get_image("calendar.png",
                                     title=t(_("Future dated sample")))
        if obj.getInvoiceExclude:
            after_icons += get_image("invoice_exclude.png",
                                     title=t(_("Exclude from invoice")))
        if obj.getHazardous:
            after_icons += get_image("hazardous.png",
                                     title=t(_("Hazardous")))

        if obj.getInternalUse:
            after_icons += get_image("locked.png", title=t(_("Internal use")))

        if after_icons:
            item['after']['getId'] = after_icons

        item['Created'] = self.ulocalized_time(obj.created, long_format=1)
        if obj.getContactUID:
            item['ClientContact'] = obj.getContactFullName
            item['replace']['ClientContact'] = "<a href='%s'>%s</a>" % \
                (obj.getContactURL, obj.getContactFullName)
        else:
            item["ClientContact"] = ""
        # TODO-performance: If SamplingWorkflowEnabled, we have to get the
        # full object to check the user permissions, so far this is
        # a performance hit.
        if obj.getSamplingWorkflowEnabled:
            # We don't do anything with Sampling Date.
            # User can modify Sampling date
            # inside AR view. In this listing view,
            # we only let the user to edit Date Sampled
            # and Sampler if he wants to make 'sample' transaction.
            if not obj.getDateSampled:
                datesampled = self.ulocalized_time(
                    DateTime(), long_format=True)
                item["class"]["getDateSampled"] = "provisional"
            else:
                datesampled = self.ulocalized_time(obj.getDateSampled,
                                                   long_format=True)

            sampler = obj.getSampler
            if sampler:
                item["replace"]["getSampler"] = obj.getSamplerFullName
            if "Sampler" in self.roles and not sampler:
                sampler = self.member.id
                item["class"]["getSampler"] = "provisional"
            # sampling workflow - inline edits for Sampler and Date Sampled
            if item["review_state"] == 'to_be_sampled':
                # We need to get the full object in order to check
                # the permissions
                full_object = obj.getObject()
                checkPermission =\
                    self.context.portal_membership.checkPermission

                # TODO Do we really need this check?
                if checkPermission(TransitionSampleSample, full_object):
                    item["required"] = ["getSampler", "getDateSampled"]
                    item["allow_edit"] = ["getSampler", "getDateSampled"]
                    # TODO-performance: hit performance while getting the
                    # sample object...
                    # TODO Can LabManagers be a Sampler?!
                    samplers = getUsers(full_object, ["Sampler", ])
                    username = self.member.getUserName()
                    users = [({
                        "ResultValue": u,
                        "ResultText": samplers.getValue(u)}) for u in samplers]
                    item['choices'] = {'getSampler': users}
                    Sampler = sampler and sampler or \
                        (username in samplers.keys() and username) or ''
                    sampler = Sampler
                else:
                    datesampled = self.ulocalized_time(obj.getDateSampled,
                                                       long_format=True)
                    sampler = obj.getSamplerFullName if obj.getSampler else ''
        else:
            datesampled = self.ulocalized_time(obj.getDateSampled,
                                               long_format=True)
            sampler = ""
        item["getDateSampled"] = datesampled
        item["getSampler"] = sampler

        # These don't exist on ARs
        # XXX This should be a list of preservers...
        item["getPreserver"] = ""
        item["getDatePreserved"] = ""

        # Advanced partitioning
        # append the UID of the primary AR as parent
        item["parent"] = obj.getRawParentAnalysisRequest or ""

        # append partition UIDs of this AR as children
        item["children"] = []
        if self.show_partitions:
            item["children"] = obj.getDescendantsUIDs or []

        return item

    @property
    def copy_to_new_allowed(self):
        mtool = api.get_tool("portal_membership")
        if mtool.checkPermission(AddAnalysisRequest, self.context):
            return True
        return False

    def getDefaultAddCount(self):
        return self.context.bika_setup.getDefaultNumberOfARsToAdd()

    @property
    def show_partitions(self):
        if api.get_current_client():
            # If current user is a client contact, delegate to ShowPartitions
            return api.get_setup().getShowPartitions()
        return True
