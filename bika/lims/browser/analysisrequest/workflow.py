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

    def notify_ar_retract(self, ar, newar):
        bika_setup = api.get_bika_setup()
        laboratory = bika_setup.laboratory
        lab_address = "<br/>".join(laboratory.getPrintAddress())
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = t(_("Erroneus result publication from ${request_id}",
                                mapping={"request_id": ar.getId()}))
        mime_msg['From'] = formataddr(
            (encode_header(laboratory.getName()),
             laboratory.getEmailAddress()))
        to = []
        contact = ar.getContact()
        if contact:
            to.append(formataddr((encode_header(contact.Title()),
                                  contact.getEmailAddress())))
        for cc in ar.getCCContact():
            formatted = formataddr((encode_header(cc.Title()),
                                   cc.getEmailAddress()))
            if formatted not in to:
                to.append(formatted)

        managers = self.context.portal_groups.getGroupMembers('LabManagers')
        for bcc in managers:
            user = self.portal.acl_users.getUser(bcc)
            if user:
                uemail = user.getProperty('email')
                ufull = user.getProperty('fullname')
                formatted = formataddr((encode_header(ufull), uemail))
                if formatted not in to:
                    to.append(formatted)
        mime_msg['To'] = ','.join(to)
        aranchor = "<a href='%s'>%s</a>" % (ar.absolute_url(),
                                            ar.getId())
        naranchor = "<a href='%s'>%s</a>" % (newar.absolute_url(),
                                             newar.getId())
        addremarks = ('addremarks' in self.request and ar.getRemarks()) and ("<br/><br/>" + _("Additional remarks:") +
                                                                             "<br/>" + ar.getRemarks().split("===")[1].strip() +
                                                                             "<br/><br/>") or ''
        sub_d = dict(request_link=aranchor,
                     new_request_link=naranchor,
                     remarks=addremarks,
                     lab_address=lab_address)
        body = Template("Some errors have been detected in the results report "
                        "published from the Sample $request_link. The Analysis "
                        "Request $new_request_link has been created automatically and the "
                        "previous has been invalidated.<br/>The possible mistake "
                        "has been picked up and is under investigation.<br/><br/>"
                        "$remarks $lab_address").safe_substitute(sub_d)
        msg_txt = MIMEText(safe_unicode(body).encode('utf-8'),
                           _subtype='html')
        mime_msg.preamble = 'This is a multi-part MIME message.'
        mime_msg.attach(msg_txt)
        try:
            host = getToolByName(self.context, 'MailHost')
            host.send(mime_msg.as_string(), immediate=True)
        except Exception as msg:
            message = _('Unable to send an email to alert lab '
                        'client contacts that the Sample has been '
                        'retracted: ${error}',
                        mapping={'error': safe_unicode(msg)})
            self.context.plone_utils.addPortalMessage(message, 'warning')

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
            keyword = service.getKeyword()
            results_range = ResultsRangeDict(keyword=keyword, uid=service_uid)
            results_range.update({
                "min": form["min"][0][service_uid],
                "max": form["max"][0][service_uid],
                "warn_min": form["warn_min"][0][service_uid],
                "warn_max": form["warn_max"][0][service_uid],
            })
            specs[service_uid] = results_range

        if ar.setAnalyses(objects_uids, prices=prices, specs=specs.values()):
            doActionFor(ar, "rollback_to_receive")

        # Reindex the analyses
        for analysis in ar.objectValues("Analysis"):
            analysis.reindexObject()

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.destination_url = self.context.absolute_url()
        self.request.response.redirect(self.destination_url)

    def workflow_action_sample(self):
        # TODO Workflow - Analysis Request - this should be managed by the guard
        if IAnalysisRequest.providedBy(self.context):
            objects = [{api.get_uid(self.context): self.context}]
        else:
            objects = self._get_selected_items(filter_active=True)
        transitioned = []
        for uid, ar in objects.items():
            sampler = self.get_form_value("Sampler", uid, default="")
            sampled = self.get_form_value("getDateSampled", uid, default="")
            if not sampler or not sampled:
                continue
            ar.setSampler(sampler)
            ar.setDateSampled(DateTime(sampled))
            success, message = doActionFor(ar, "sample")
            if success:
                transitioned.append(ar.getId())
        message = _("No changes made")
        if transitioned:
            message = _("Saved items: {}".format(", ".join(transitioned)))
        self.redirect(message=message)

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

    def requires_partitioning(self, brain_or_object):
        """Returns whether the passed in object needs to be partitioned
        """
        obj = api.get_object(brain_or_object)
        if not IAnalysisRequest.providedBy(obj):
            return False
        template = obj.getTemplate()
        if not template:
            return False
        return template.getAutoPartition()

    def workflow_action_receive(self):
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        items = [self.context,] if came_from == 'workflow_action' \
                else self._get_selected_items().values()
        trans, dest = self.submitTransition(action, came_from, items)
        with_partitions = filter(self.requires_partitioning, items)
        if with_partitions:
            # Redirect to the partitioning magic view
            back_url = self.context.absolute_url()
            uids = ",".join(map(api.get_uid, with_partitions))
            url = "{}/partition_magic?uids={}".format(back_url, uids)
            self.request.response.redirect(url)
        elif trans and 'receive' in self.context.bika_setup.getAutoPrintStickers():
            transitioned = [item.UID() for item in items]
            tmpl = self.context.bika_setup.getAutoStickerTemplate()
            q = "/sticker?autoprint=1&template=%s&items=" % tmpl
            q += ",".join(transitioned)
            self.request.response.redirect(self.context.absolute_url() + q)
        elif trans:
            message = PMF('Changes saved.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)

    def workflow_action_submit(self):
        AnalysesWorkflowAction.workflow_action_submit(self)
        checkPermission = self.context.portal_membership.checkPermission
        if checkPermission(EditResults, self.context):
            self.destination_url = self.context.absolute_url() + "/manage_results"
        else:
            self.destination_url = self.context.absolute_url()
        self.request.response.redirect(self.destination_url)

    def workflow_action_prepublish(self):
        self.workflow_action_publish()

    def workflow_action_republish(self):
        self.workflow_action_publish()

    def workflow_action_print(self):
        # Calls printLastReport method for selected ARs
        uids = self.request.get('uids',[])
        uc = getToolByName(self.context, 'uid_catalog')
        for obj in uc(UID=uids):
            ar=obj.getObject()
            ar.printLastReport()
        referer = self.request.get_header("referer")
        self.request.response.redirect(referer)

    def workflow_action_publish(self):
        if not isActive(self.context):
            message = _('Item is inactive.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(self.context.absolute_url())
            return
        # AR publish preview
        uids = self.request.form.get('uids', [self.context.UID()])
        items = ",".join(uids)
        self.request.response.redirect(
            self.context.portal_url() + "/analysisrequests/publish?items="
            + items)

    def workflow_action_verify(self):
        # default bika_listing.py/WorkflowAction, but then go to view screen.
        self.destination_url = self.context.absolute_url()
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        if type(came_from) in (list, tuple):
            came_from = came_from[0]
        return self.workflow_action_default(action='verify', came_from=came_from)

    def workflow_action_invalidate(self):
        # AR should be retracted
        # Can't transition inactive ARs
        if not api.is_active(self.context):
            message = _('Item is inactive.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(self.context.absolute_url())
            return

        # Retract the AR and get the retest
        api.do_transition_for(self.context, 'invalidate')
        retest = self.context.getRetest()

        # 4. The system immediately alerts the client contacts who ordered
        # the results, per email and SMS, that a possible mistake has been
        # picked up and is under investigation.
        # A much possible information is provided in the email, linking
        # to the AR online.
        bika_setup = api.get_bika_setup()
        if bika_setup.getNotifyOnARRetract():
            self.notify_ar_retract(self.context, retest)

        message = _('${items} invalidated.',
                    mapping={'items': self.context.getId()})
        self.context.plone_utils.addPortalMessage(message, 'warning')
        self.request.response.redirect(retest.absolute_url())

    def workflow_action_copy_to_new(self):
        # Pass the selected AR UIDs in the request, to ar_add.
        objects = WorkflowAction._get_selected_items(self)
        if not objects:
            message = _("No analyses have been selected")
            self.context.plone_utils.addPortalMessage(message, 'info')
            referer = self.request.get_header("referer")
            self.request.response.redirect(referer)
            return
        url = self.context.absolute_url() + "/ar_add" + \
            "?ar_count={0}".format(len(objects)) + \
            "&copy_from={0}".format(",".join(objects.keys()))
        self.request.response.redirect(url)
        return

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

    def workflow_action_create_partitions(self):
        """Redirects the user to the partition magic view
        """
        uids = list()
        if IAnalysisRequest.providedBy(self.context):
            uids = [api.get_uid(self.context)]
        else:
            uids = self.get_selected_uids()
        if not uids:
            message = "No items selected".format(repr(type(self.context)))
            self.redirect(message=message, level="error")

        # Redirect to the partitioning magic view
        url = "{}/partition_magic?uids={}".format(self.back_url, ",".join(uids))
        self.redirect(redirect_url=url)
