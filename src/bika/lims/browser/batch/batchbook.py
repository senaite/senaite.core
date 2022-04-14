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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import re
from collections import OrderedDict
from collections import defaultdict
from operator import itemgetter

from bika.lims import api
from bika.lims.utils import get_link_for
from bika.lims import bikaMessageFactory as _
from bika.lims.api.security import check_permission
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IBatchBookView
from bika.lims.permissions import AddAnalysisRequest
from bika.lims.permissions import FieldEditAnalysisResult
from bika.lims.utils import t
from Products.CMFCore.permissions import ModifyPortalContent
from zope.interface import implementer

DESCRIPTION = _("The batch book allows to introduce analysis results for all "
                "samples in this batch. Please note that submitting the "
                "results for verification is only possible within samples or "
                "worksheets, because additional information like e.g. the "
                "instrument or the method need to be set additionally.")


@implementer(IBatchBookView)
class BatchBookView(BikaListingView):

    def __init__(self, context, request):
        super(BatchBookView, self).__init__(context, request)

        self.context_actions = {}
        self.contentFilter = {"sort_on": "created"}
        self.title = context.Title()
        self.description = t(DESCRIPTION)

        self.show_select_column = True
        self.show_search = False
        self.pagesize = 999999
        self.form_id = "batchbook"
        self.show_categories = True
        self.expand_all_categories = True
        self.show_column_toggles = False

        self.icon = "{}{}".format(
            self.portal_url, "/senaite_theme/icon/batchbook")

        self.columns = OrderedDict((
            ("AnalysisRequest", {
                "title": _("Sample"),
                "sortable": False,
            }),
            ("SampleType", {
                "title": _("Sample Type"),
                "sortable": False,
            }),
            ("SamplePoint", {
                "title": _("Sample Point"),
                "sortable": False,
            }),
            ("ClientOrderNumber", {
                "title": _("Client Order Number"),
                "sortable": False,
            }),
            ("created", {
                "title": _("Date Registered"),
                "sortable": False,
            }),
            ("state_title", {
                "title": _("State"),
                "index": "review_state",
                "sortable": False,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys()
            },
        ]

    def is_copy_to_new_allowed(self):
        """Checks if it is allowed to copy the sample
        """
        if check_permission(AddAnalysisRequest, self.context):
            return True
        return False

    def can_edit_analysis_result(self, analysis):
        """Checks if the current user can edit the analysis result
        """
        return check_permission(FieldEditAnalysisResult, analysis)

    def update(self):
        """Update hook
        """
        super(BatchBookView, self).update()
        # check if the use can modify
        self.allow_edit = check_permission(ModifyPortalContent, self.context)
        # append copy to new transition
        if self.is_copy_to_new_allowed():
            self.add_copy_transition()

    def add_copy_transition(self):
        """Add copy transtion
        """
        review_states = []
        for review_state in self.review_states:
            custom_transitions = review_state.get("custom_transitions", [])
            base_url = api.get_url(self.context)
            custom_transitions.append({
                "id": "copy_to_new",
                "title": _("Copy to new"),
                "url": "{}/workflow_action?action=copy_to_new".format(base_url)
            })
            review_state["custom_transitions"] = custom_transitions
            review_states.append(review_state)
        self.review_states = review_states

    def before_render(self):
        """Before render hook
        """
        super(BatchBookView, self).before_render()

    def folderitems(self):
        """Accumulate a list of all AnalysisRequest objects contained in
        this Batch, as well as those which are inherited.
        """
        ars = self.context.getAnalysisRequests(is_active=True)
        self.total = len(ars)

        self.categories = []
        analyses = defaultdict(list)
        items = []
        distinct = []  # distinct analyses (each one a different service)
        keywords = []
        for ar in ars:
            for analysis in ar.getAnalyses(full_objects=True):
                analyses[ar.getId()].append(analysis)
                if analysis.getKeyword() not in keywords:
                    # we use a keyword check, because versioned services are !=.
                    keywords.append(analysis.getKeyword())
                    distinct.append(analysis)

            batchlink = ""
            batch = ar.getBatch()
            if batch:
                batchlink = get_link_for(batch)

            arlink = get_link_for(ar)

            subgroup = ar.getSubGroup()
            sub_title = subgroup.Title() if subgroup else t(_("No Subgroup"))
            sub_sort = subgroup.getSortKey() if subgroup else "1"
            sub_class = re.sub(r"[^A-Za-z\w\d\-\_]", "", sub_title)

            if [sub_sort, sub_title] not in self.categories:
                self.categories.append([sub_sort, sub_title])

            wf = api.get_tool("portal_workflow")
            review_state = api.get_review_status(ar)
            state_title = wf.getTitleForStateOnType(
                review_state, "AnalysisRequest")

            item = {
                "obj": ar,
                "id": ar.id,
                "uid": ar.UID(),
                "category": sub_title,
                "title": ar.Title(),
                "type_class": "contenttype-AnalysisRequest",
                "url": ar.absolute_url(),
                "relative_url": ar.absolute_url(),
                "view_url": ar.absolute_url(),
                "created": self.ulocalized_time(ar.created(), long_format=1),
                "sort_key": ar.created(),
                "replace": {
                    "Batch": batchlink,
                    "AnalysisRequest": arlink,
                },
                "before": {},
                "after": {},
                "choices": {},
                "class": {"Batch": "Title"},
                "state_class": "state-active subgroup_{0}".format(sub_class) if sub_class else "state-active",
                "allow_edit": [],
                "Batch": "",
                "SamplePoint": ar.getSamplePoint().Title() if ar.getSamplePoint() else "",
                "SampleType": ar.getSampleType().Title() if ar.getSampleType() else "",
                "ClientOrderNumber": ar.getClientOrderNumber(),
                "AnalysisRequest": "",
                "state_title": state_title,
            }
            items.append(item)

        unitstr = '<em class="discreet" style="white-space:nowrap;">%s</em>'

        # Insert columns for analyses
        for d_a in distinct:
            keyword = d_a.getKeyword()
            short = d_a.getShortTitle()
            title = d_a.Title()

            self.columns[keyword] = {
                "title":  short if short else title,
                "sortable": False,
            }
            self.review_states[0]["columns"].insert(
                len(self.review_states[0]["columns"]) - 1, keyword)

            # Insert values for analyses
            for i, item in enumerate(items):
                for analysis in analyses[item["id"]]:
                    if keyword not in items[i]:
                        items[i][keyword] = ""
                    if analysis.getKeyword() != keyword:
                        continue

                    # check if the user can edit the analysis result
                    can_edit_result = self.can_edit_analysis_result(analysis)

                    calculation = analysis.getCalculation()
                    if self.allow_edit and can_edit_result and not calculation:
                        items[i]["allow_edit"].append(keyword)
                        self.columns[keyword]["ajax"] = True

                    value = analysis.getResult()
                    items[i][keyword] = value
                    items[i]["class"][keyword] = ""

                    if value or (can_edit_result and not calculation):
                        unit = unitstr % d_a.getUnit()
                        items[i]["after"][keyword] = unit

                if keyword not in items[i]["class"]:
                    items[i]["class"][keyword] = "empty"

        self.categories.sort()
        self.categories = [x[1] for x in self.categories]

        items = sorted(items, key=itemgetter("sort_key"), reverse=True)

        return items
