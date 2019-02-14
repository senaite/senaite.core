# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import plone
from bika.lims.browser.analyses.workflow import AnalysesWorkflowAction
from bika.lims.browser.bika_listing import WorkflowAction


# TODO Revisit AnalysisRequestWorkflowAction class
# This class is not only used for workflow actions taken in AnalysisRequest
# context, but also for workflow actions taken in other contexts (e.g.Client or
# Batch) where the triggered action is for Analysis Requests selected from a
# listing. E.g: ClientWorkflowAction and BatchWorkflowAction.
class AnalysisRequestWorkflowAction(AnalysesWorkflowAction):
    """Workflow actions taken in AnalysisRequest context.
    """

    def __call__(self):
        return self.redirect(message="AnalysisRequestWorkflowAction",
                             level="error")

        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        if type(action) in (list, tuple):
            action = action[0]
        if type(came_from) in (list, tuple):
            came_from = came_from[0]
        # Call out to the workflow action method
        # Use default bika_listing.py/WorkflowAction for other transitions
        method_name = 'workflow_action_' + action if action else ''
        method = getattr(self, method_name, False)
        if method:
            method()
        else:
            WorkflowAction.__call__(self)
