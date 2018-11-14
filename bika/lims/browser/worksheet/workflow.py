# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from operator import attrgetter

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses.workflow import AnalysesWorkflowAction
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.permissions import ManageWorksheets
from bika.lims.subscribers import skip
from plone.protect import CheckAuthenticator


class WorksheetFolderWorkflowAction(WorkflowAction):
    """Workflow actions taken in the WorksheetFolder

    This function is called to do the workflow actions that apply to worksheets
    in the WorksheetFolder
    """
    def __call__(self):
        form = self.request.form
        CheckAuthenticator(form)
        action, came_from = WorkflowAction._get_form_workflow_action(self)

        if action == "reassign":
            mtool = api.get_tool("portal_membership")
            if not mtool.checkPermission(ManageWorksheets, self.context):
                # Redirect to WS list
                msg = _("You do not have sufficient privileges to "
                        "manage worksheets.")
                self.context.plone_utils.addPortalMessage(msg, "warning")
                portal = api.get_portal()
                self.destination_url = portal.absolute_url() + "/worksheets"
                self.request.response.redirect(self.destination_url)
                return

            selected_worksheets = WorkflowAction._get_selected_items(self)
            selected_worksheet_uids = selected_worksheets.keys()

            if selected_worksheets:
                changes = False
                for uid in selected_worksheet_uids:
                    worksheet = selected_worksheets[uid]
                    # Double-check the state first
                    if api.get_workflow_status_of(worksheet) == "open":
                        analyst = form["Analyst"][0][uid]
                        worksheet.setAnalyst(analyst)
                        worksheet.reindexObject(idxs=["getAnalyst"])
                        changes = True
                if changes:
                    message = _("Changes saved.")
                    self.context.plone_utils.addPortalMessage(message, "info")

            self.destination_url = self.request.get_header(
                "referer", self.context.absolute_url())
            self.request.response.redirect(self.destination_url)
        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)


class WorksheetWorkflowAction(AnalysesWorkflowAction):
    """Workflow actions taken in Worksheets

    This function is called to do the worflow actions that apply to analyses in
    worksheets
    """
    def __call__(self):
        form = self.request.form
        CheckAuthenticator(form)
        bac = api.get_tool("bika_analysis_catalog")
        action, came_from = WorkflowAction._get_form_workflow_action(self)

        if action == "submit":
            # Submit the form. Saves the results, methods, etc.
            # Calls to its parent class AnalysesWorkflowAction
            self.workflow_action_submit()

        # assign
        elif action == "assign":
            if not self.context.checkUserManage():
                self.request.response.redirect(self.context.absolute_url())
                return

            analysis_uids = form.get("uids", [])
            if analysis_uids:
                # We retrieve the analyses from the database sorted by AR ID
                # ascending, so the positions of the ARs inside the WS are
                # consistent with the order of the ARs
                catalog = api.get_tool(CATALOG_ANALYSIS_LISTING)
                brains = catalog({
                    "UID": analysis_uids,
                    "sort_on": "getRequestID"})

                # Now, we need the analyses within a request ID to be sorted by
                # sortkey (sortable_title index), so it will appear in the same
                # order as they appear in Analyses list from AR view
                curr_arid = None
                curr_brains = []
                sorted_brains = []
                for brain in brains:
                    arid = brain.getRequestID
                    if curr_arid != arid:
                        # Sort the brains we've collected until now, that
                        # belong to the same Analysis Request
                        curr_brains.sort(key=attrgetter("getPrioritySortkey"))
                        sorted_brains.extend(curr_brains)
                        curr_arid = arid
                        curr_brains = []

                    # Now we are inside the same AR
                    curr_brains.append(brain)
                    continue

                # Sort the last set of brains we've collected
                curr_brains.sort(key=attrgetter('getPrioritySortkey'))
                sorted_brains.extend(curr_brains)

                # Add analyses in the worksheet
                self.context.addAnalyses(sorted_brains)

            self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)

        # unassign
        elif action == "unassign":
            if not self.context.checkUserManage():
                self.request.response.redirect(self.context.absolute_url())
                return

            selected_analyses = WorkflowAction._get_selected_items(self)
            selected_analysis_uids = selected_analyses.keys()

            for analysis_uid in selected_analysis_uids:
                try:
                    analysis = bac(UID=analysis_uid)[0].getObject()
                except IndexError:
                    # Duplicate analyses are removed when their analyses
                    # get removed, so indexerror is expected.
                    continue
                if skip(analysis, action, peek=True):
                    continue
                self.context.removeAnalysis(analysis)

            message = _("Changes saved.")
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)

        # verify
        elif action == "verify":
            # default bika_listing.py/WorkflowAction, but then go to view
            # screen.
            self.destination_url = self.context.absolute_url()
            return self.workflow_action_default(
                action="verify", came_from=came_from)
        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)
