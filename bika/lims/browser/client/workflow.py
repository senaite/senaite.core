# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import plone
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.analysisrequest import AnalysisRequestWorkflowAction
from bika.lims.utils import isActive


class ClientWorkflowAction(AnalysisRequestWorkflowAction):
    """ This function is called to do the worflow actions
        that apply to objects transitioned directly from Client views

        The main lab 'analysisrequests' and 'samples' views also have
        workflow_action urls bound to this handler.

        The parent AnalysisRequestWorkflowAction handles
        AR and Sample context workflow actions (affecting parts/analyses)

    """
    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        self.context = aq_inner(self.context)
        workflow = getToolByName(self.context, 'portal_workflow')
        checkPermission = self.context.portal_membership.checkPermission
        context = self.context
        context_url = context.absolute_url()

        # TODO Workflow - AR + Sample - Revisit/remove all this crap
        # use came_from to decide which UI action was clicked.
        # "workflow_action" is the action name specified in the
        # portal_workflow transition url.
        came_from = "workflow_action"
        action = form.get(came_from, '')
        if not action:
            # workflow_action_button is the action name specified in
            # the bika_listing_view table buttons.
            came_from = "workflow_action_button"
            action = form.get('workflow_action_id', '')
            if not action:
                if self.destination_url == "":
                    self.destination_url = self.request.get_header("referer",
                                                                   context_url)
                self.request.response.redirect(self.destination_url)
                return

        elif action in ('prepublish', 'publish', 'republish'):
            # We pass a list of AR objects to Publish.
            # it returns a list of AR IDs which were actually published.
            objects = AnalysisRequestWorkflowAction._get_selected_items(self)
            its = []
            for uid, obj in objects.items():
                if isActive(obj):
                    its.append(uid)
            its = ",".join(its)
            q = "/publish?items=" + its
            self.destination_url = self.context.absolute_url() + q
            self.request.response.redirect(self.destination_url)

        else:
            AnalysisRequestWorkflowAction.__call__(self)
