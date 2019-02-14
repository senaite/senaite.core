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
from bika.lims.workflow import ActionHandlerPool, doActionFor
from plone.protect import CheckAuthenticator


class WorksheetFolderWorkflowAction(WorkflowAction):
    """Workflow actions taken in the WorksheetFolder

    This function is called to do the workflow actions that apply to worksheets
    in the WorksheetFolder
    """
    def __call__(self):

        return self.redirect(message="WorksheetFolderWorkflowAction",
                             level="error")

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

        return self.redirect(message="WorksheetWorkflowAction",
                             level="error")

        form = self.request.form
        CheckAuthenticator(form)
        analysis_uids = form.get("uids", [])
        if not analysis_uids:
            self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)
            return

        action, came_from = WorkflowAction._get_form_workflow_action(self)

        if action == "submit":
            # Submit the form. Saves the results, methods, etc.
            # Calls to its parent class AnalysesWorkflowAction
            self.workflow_action_submit()
