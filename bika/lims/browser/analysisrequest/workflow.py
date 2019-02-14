# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

import plone
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import PMF, api
from bika.lims import bikaMessageFactory as _
from bika.lims import interfaces
from bika.lims.browser.analyses.workflow import AnalysesWorkflowAction
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.content.analysisspec import ResultsRangeDict
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.permissions import *
from bika.lims.utils import encode_header
from bika.lims.utils import isActive
from bika.lims.utils import t
from bika.lims.workflow import doActionFor
from email.Utils import formataddr


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

    def get_specs_value(self, service, specs_key, default=None):
        """Returns the specification value for the specs_key (min, max, etc.)
        that must be assigned to new analyses for the service passed in
        """
        uid = api.get_uid(service)
        spec_value = self.request.form.get(specs_key, [{}])[0].get(uid, None)
        if spec_value is None and default is not None:
            return default
        return spec_value

    def get_specs(self, service):
        """Returns the analysis specs to assign to analyses created by using
        the service passed in. It overrides the specs of the service with the
        specs set manually in the manage analyses form (if any).
        """
        keyword = service.getKeyword()
        uid = api.get_uid(service)
        specs_keys = ("min", "max", "warn_min", "warn_max", "min_operator",
                      "max_operator")
        specs = ResultsRangeDict(keyword=keyword, uid=uid).copy()
        for specs_key in specs_keys:
            default = specs.get(specs_key, "")
            specs[specs_key] = self.get_specs_value(service, specs_key, default)
        return specs

    def workflow_action_save_analyses_button(self):
        form = self.request.form
        # AR Manage Analyses: save Analyses
        ar = self.context
        objects = WorkflowAction._get_selected_items(self)
        objects_uids = objects.keys()
        prices = form.get("Price", [None])[0]

        # Hidden analyses?
        # https://jira.bikalabs.com/browse/LIMS-1324
        outs = []
        hidden_ans = form.get('Hidden', {})
        for uid in objects.keys():
            hidden = hidden_ans.get(uid, '') == "on" or False
            outs.append({'uid': uid, 'hidden': hidden})
        ar.setAnalysisServicesSettings(outs)

        specs = {}
        for service_uid, service in objects.items():
            specs[service_uid] = self.get_specs(service)

        if ar.setAnalyses(objects_uids, prices=prices, specs=specs.values()):
            doActionFor(ar, "rollback_to_receive")

        # Reindex the analyses
        for analysis in ar.objectValues("Analysis"):
            analysis.reindexObject()

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.destination_url = self.context.absolute_url()
        self.request.response.redirect(self.destination_url)


    def workflow_action_preserve(self):
        # TODO Workflow - Analysis Request - this should be managed by the guard
        if IAnalysisRequest.providedBy(self.context):
            objects = [{api.get_uid(self.context): self.context}]
        else:
            objects = self._get_selected_items(filter_active=True,
                                               permissions=[PreserveSample])
        transitioned = []
        for uid, ar in objects.items():
            preserver = self.get_form_value("Preserver", uid, default="")
            preserved = self.get_form_value("getDatePreserved", uid, default="")
            if not preserver or not preserved:
                continue
            ar.setPreserver(preserver)
            ar.setDatePreserved(DateTime(preserved))
            success, message = doActionFor(ar, "preserve")
            if success:
                transitioned.append(ar.getId())
        message = _("No changes made")
        if transitioned:
            message = _("Saved items: {}".format(", ".join(transitioned)))
        self.redirect(message=message)

    def workflow_action_schedule_sampling(self):
        """
        This function prevent the transition if the fields "SamplingDate"
        and "ScheduledSamplingSampler" are uncompleted.
        :returns: bool
        """
        from bika.lims.utils.workflow import schedulesampling
        message = 'Not expected transition.'
        # In Samples Folder we have to get each selected item
        if interfaces.ISamplesFolder.providedBy(self.context):
            select_objs = WorkflowAction._get_selected_items(self)
            message = _('Transition done.')
            for key in select_objs.keys():
                sample = select_objs[key]
                # Getting the sampler
                sch_sampl = self.request.form.get(
                    'getScheduledSamplingSampler', None)[0].get(key) if\
                    self.request.form.get(
                        'getScheduledSamplingSampler', None) else ''
                # Getting the date
                sampl_date = self.request.form.get(
                    'getSamplingDate', None)[0].get(key) if\
                    self.request.form.get(
                        'getSamplingDate', None) else ''
                # Setting both values
                sample.setScheduledSamplingSampler(sch_sampl)
                sample.setSamplingDate(sampl_date)
                # Transitioning the sample
                success, errmsg = schedulesampling.doTransition(sample)
                if errmsg == 'missing':
                    message = _(
                        "'Sampling date' and 'Define the Sampler for the" +
                        " scheduled sampling' must be completed and saved " +
                        "in order to schedule a sampling. Element: %s" %
                        sample.getId())
                elif errmsg == 'cant_trans':
                    message = _(
                        "The item %s can't be transitioned." % sample.getId())
                else:
                    message = _('Transition done.')
                self.context.plone_utils.addPortalMessage(message, 'info')
        else:
            success, errmsg = schedulesampling.doTransition(self.context)
            if errmsg == 'missing':
                message = _(
                    "'Sampling date' and 'Define the Sampler for the" +
                    " scheduled sampling' must be completed and saved in " +
                    "order to schedule a sampling.")
            elif errmsg == 'cant_trans':
                message = _("The item can't be transitioned.")
            else:
                message = _('Transition done.')
            self.context.plone_utils.addPortalMessage(message, 'info')
        # Reload the page in order to show the portal message
        self.request.response.redirect(self.context.absolute_url())
        return success

