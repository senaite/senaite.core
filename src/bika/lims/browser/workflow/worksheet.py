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

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.workflow import WorkflowActionGenericAdapter
from bika.lims.interfaces import IWorksheet


class WorkflowActionAssignAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of assignment of analyses into a worksheet
    """

    def __call__(self, action, analyses):
        worksheet = self.context
        if not IWorksheet.providedBy(worksheet):
            return self.redirect(message=_("No changes made"), level="warning")

        # Sort the analyses by AR ID ascending + priority sort key, so the
        # positions of the ARs inside the WS are consistent with ARs order
        sorted_analyses = self.sorted_analyses(analyses)

        # Add analyses into the worksheet
        worksheet.addAnalyses(sorted_analyses)

        # Redirect the user to success page
        return self.success([worksheet])

    def sorted_analyses(self, analyses):
        """Sort the analyses by AR ID ascending and subsorted by priority
        sortkey within the AR they belong to
        """
        analyses = sorted(analyses, key=lambda an: an.getRequestID())

        def sorted_by_sortkey(objs):
            return sorted(objs, key=lambda an: an.getPrioritySortkey())

        # Now, we need the analyses within a request ID to be sorted by
        # sortkey (sortable_title index), so it will appear in the same
        # order as they appear in Analyses list from AR view
        current_sample_id = None
        current_analyses = []
        sorted_analyses = []
        for analysis in analyses:
            sample_id = analysis.getRequestID()
            if sample_id and current_sample_id != sample_id:
                # Sort the brains we've collected until now, that
                # belong to the same Analysis Request
                current_analyses = sorted_by_sortkey(current_analyses)
                sorted_analyses.extend(current_analyses)
                current_sample_id = sample_id
                current_analyses = []

            # Now we are inside the same AR
            current_analyses.append(analysis)
            continue

        # Sort the last set of brains we've collected
        current_analyses = sorted_by_sortkey(current_analyses)
        sorted_analyses.extend(current_analyses)
        return sorted_analyses


class WorkflowActionReassignAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of reassignment of an Analyst to a worksheet
    """

    def __call__(self, action, objects):
        # Assign the Analyst
        transitioned = filter(lambda obj: self.set_analyst(obj), objects)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        # Redirect the user to success page
        return self.success(transitioned)

    def set_analyst(self, worksheet):
        analyst = self.get_form_value("Analyst", worksheet)
        if not analyst:
            # Cannot reassign if no analyst is set
            return False
        worksheet.setAnalyst(analyst)
        worksheet.reindexObject(idxs=["getAnalyst"])
        return True
