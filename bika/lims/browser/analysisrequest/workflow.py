# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

import plone
import zope.event
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from bika.lims import PMF, api
from bika.lims import bikaMessageFactory as _
from bika.lims import interfaces
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.idserver import renameAfterCreation
from bika.lims.permissions import *
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import copy_field_values
from bika.lims.utils import encode_header
from bika.lims.utils import isActive
from bika.lims.utils import t
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from bika.lims.workflow import getCurrentState
from bika.lims.workflow import wasTransitionPerformed
from email.Utils import formataddr


class AnalysisRequestWorkflowAction(WorkflowAction):

    """Workflow actions taken in AnalysisRequest context.

        Sample context workflow actions also redirect here
        Applies to
            Analysis objects
            SamplePartition objects
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
                        "published from the Analysis Request $request_link. The Analysis "
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
                        'client contacts that the Analysis Request has been '
                        'retracted: ${error}',
                        mapping={'error': safe_unicode(msg)})
            self.context.plone_utils.addPortalMessage(message, 'warning')

    def workflow_action_save_partitions_button(self):
        form = self.request.form
        # Sample Partitions or AR Manage Analyses: save Partition Table
        sample = self.context.portal_type == 'Sample' and self.context or\
            self.context.getSample()
        part_prefix = sample.getId() + "-P"
        nr_existing = len(sample.objectIds())
        nr_parts = len(form['PartTitle'][0])
        # add missing parts
        if nr_parts > nr_existing:
            for i in range(nr_parts - nr_existing):
                part = _createObjectByType("SamplePartition", sample, tmpID())
                part.setDateReceived = DateTime()
                part.processForm()
        # remove excess parts
        if nr_existing > nr_parts:
            for i in range(nr_existing - nr_parts):
                part = sample['%s%s' % (part_prefix, nr_existing - i)]
                analyses = part.getAnalyses()
                for a in analyses:
                    a.setSamplePartition(None)
                sample.manage_delObjects(['%s%s' % (part_prefix, nr_existing - i), ])
        # modify part container/preservation
        for part_uid, part_id in form['PartTitle'][0].items():
            part = sample["%s%s" % (part_prefix, part_id.split(part_prefix)[1])]
            part.edit(
                Container=form['getContainer'][0][part_uid],
                Preservation=form['getPreservation'][0][part_uid],
            )
            part.reindexObject()
            # Adding the Security Seal Intact checkbox's value to the container object
            container_uid = form['getContainer'][0][part_uid]
            uc = getToolByName(self.context, 'uid_catalog')
            cbr = uc(UID=container_uid)
            if cbr and len(cbr) > 0:
                container_obj = cbr[0].getObject()
            else:
                continue
            value = form.get('setSecuritySealIntact', {}).get(part_uid, '') == 'on'
            container_obj.setSecuritySealIntact(value)
        objects = WorkflowAction._get_selected_items(self)
        if not objects:
            message = _("No items have been selected")
            self.context.plone_utils.addPortalMessage(message, 'info')
            if self.context.portal_type == 'Sample':
                # in samples his table is on 'Partitions' tab
                self.destination_url = self.context.absolute_url() +\
                    "/partitions"
            else:
                # in ar context this table is on 'ManageAnalyses' tab
                self.destination_url = self.context.absolute_url() +\
                    "/analyses"
            self.request.response.redirect(self.destination_url)

    def workflow_action_save_analyses_button(self):
        form = self.request.form
        workflow = getToolByName(self.context, 'portal_workflow')
        bsc = self.context.bika_setup_catalog
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        # AR Manage Analyses: save Analyses
        ar = self.context
        sample = ar.getSample()
        objects = WorkflowAction._get_selected_items(self)
        if not objects:
            message = _("No analyses have been selected")
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.context.absolute_url() + "/analyses"
            self.request.response.redirect(self.destination_url)
            return
        Analyses = objects.keys()
        prices = form.get("Price", [None])[0]

        # Hidden analyses?
        # https://jira.bikalabs.com/browse/LIMS-1324
        outs = []
        hiddenans = form.get('Hidden', {})
        for uid in Analyses:
            hidden = hiddenans.get(uid, '')
            hidden = True if hidden == 'on' else False
            outs.append({'uid':uid, 'hidden':hidden})
        ar.setAnalysisServicesSettings(outs)

        specs = {}
        if form.get("min", None):
            for service_uid in Analyses:
                service = objects[service_uid]
                keyword = service.getKeyword()
                specs[service_uid] = {
                    "min": form["min"][0][service_uid],
                    "max": form["max"][0][service_uid],
                    "error": form["error"][0][service_uid],
                    "keyword": keyword,
                    "uid": service_uid,
                }
        else:
            for service_uid in Analyses:
                service = objects[service_uid]
                keyword = service.getKeyword()
                specs[service_uid] = {"min": "", "max": "", "error": "",
                                      "keyword": keyword, "uid": service_uid}
        new = ar.setAnalyses(Analyses, prices=prices, specs=specs.values())
        # link analyses and partitions
        # If Bika Setup > Analyses > 'Display individual sample
        # partitions' is checked, no Partitions available.
        # https://github.com/bikalabs/Bika-LIMS/issues/1030
        if 'Partition' in form:
            for service_uid, service in objects.items():
                part_id = form['Partition'][0][service_uid]
                part = sample[part_id]
                analysis = ar[service.getKeyword()]
                analysis.setSamplePartition(part)
                analysis.reindexObject()
                partans = part.getAnalyses()
                partans.append(analysis)
                part.setAnalyses(partans)
                part.reindexObject()

        if new:
            ar_state = getCurrentState(ar)
            if wasTransitionPerformed(ar, 'to_be_verified'):
                # Apply to AR only; we don't want this transition to cascade.
                ar.REQUEST['workflow_skiplist'].append("retract all analyses")
                workflow.doActionFor(ar, 'retract')
                ar.REQUEST['workflow_skiplist'].remove("retract all analyses")
                ar_state = getCurrentState(ar)
            for analysis in new:
                changeWorkflowState(analysis, 'bika_analysis_workflow', ar_state)

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.destination_url = self.context.absolute_url()
        self.request.response.redirect(self.destination_url)

    def workflow_action_preserve(self):
        form = self.request.form
        workflow = getToolByName(self.context, 'portal_workflow')
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        checkPermission = self.context.portal_membership.checkPermission
        # Partition Preservation
        # the partition table shown in AR and Sample views sends it's
        # action button submits here.
        objects = WorkflowAction._get_selected_items(self)
        transitioned = []
        incomplete = []
        for obj_uid, obj in objects.items():
            part = obj
            # can't transition inactive items
            if workflow.getInfoFor(part, 'inactive_state', '') == 'inactive':
                continue
            if not checkPermission(PreserveSample, part):
                continue
            # grab this object's Preserver and DatePreserved from the form
            Preserver = form['getPreserver'][0][obj_uid].strip()
            Preserver = Preserver and Preserver or ''
            DatePreserved = form['getDatePreserved'][0][obj_uid].strip()
            DatePreserved = DatePreserved and DateTime(DatePreserved) or ''
            # write them to the sample
            part.setPreserver(Preserver)
            part.setDatePreserved(DatePreserved)
            # transition the object if both values are present
            if Preserver and DatePreserved:
                workflow.doActionFor(part, action)
                transitioned.append(part.id)
            else:
                incomplete.append(part.id)
            part.reindexObject()
            part.aq_parent.reindexObject()
        message = None
        if len(transitioned) > 1:
            message = _('${items} are waiting to be received.',
                        mapping={'items': safe_unicode(', '.join(transitioned))})
            self.context.plone_utils.addPortalMessage(message, 'info')
        elif len(transitioned) == 1:
            message = _('${item} is waiting to be received.',
                        mapping={'item': safe_unicode(', '.join(transitioned))})
            self.context.plone_utils.addPortalMessage(message, 'info')
        if not message:
            message = _('No changes made.')
            self.context.plone_utils.addPortalMessage(message, 'info')

        if len(incomplete) > 1:
            message = _('${items} are missing Preserver or Date Preserved',
                        mapping={'items': safe_unicode(', '.join(incomplete))})
            self.context.plone_utils.addPortalMessage(message, 'error')
        elif len(incomplete) == 1:
            message = _('${item} is missing Preserver or Preservation Date',
                        mapping={'item': safe_unicode(', '.join(incomplete))})
            self.context.plone_utils.addPortalMessage(message, 'error')

        self.destination_url = self.request.get_header("referer",
                               self.context.absolute_url())
        self.request.response.redirect(self.destination_url)

    def workflow_action_receive(self):
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        items = [self.context,] if came_from == 'workflow_action' \
                else self._get_selected_items().values()
        trans, dest = self.submitTransition(action, came_from, items)
        if trans and 'receive' in self.context.bika_setup.getAutoPrintStickers():
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
        form = self.request.form
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        checkPermission = self.context.portal_membership.checkPermission
        if not isActive(self.context):
            message = _('Item is inactive.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(self.context.absolute_url())
            return
        # calcs.js has kept item_data and form input interim values synced,
        # so the json strings from item_data will be the same as the form values
        item_data = {}
        if 'item_data' in form:
            if isinstance(form['item_data'], list):
                for i_d in form['item_data']:
                    for i, d in json.loads(i_d).items():
                        item_data[i] = d
            else:
                item_data = json.loads(form['item_data'])
        selected_analyses = WorkflowAction._get_selected_items(self)
        results = {}
        hasInterims = {}
        # check that the form values match the database
        # save them if not.
        for uid, result in self.request.form.get('Result', [{}])[0].items():
            # Do not save data for analyses that are not selected.
            if uid not in selected_analyses:
                continue
            analysis = selected_analyses[uid]
            # never save any part of rows with empty result values.
            # https://jira.bikalabs.com/browse/LIMS-1944:
            if not result:
                continue
            # ignore result if analysis object no longer exists
            if not analysis:
                continue
            # Prevent saving data if the analysis is already transitioned
            if not (checkPermission(EditResults, analysis) or checkPermission(EditFieldResults, analysis)):
                title = safe_unicode(analysis.Title())
                msgid = _('Result for ${analysis} could not be saved because '
                          'it was already submitted by another user.',
                          mapping={'analysis': title})
                message = safe_unicode(t(msgid))
                self.context.plone_utils.addPortalMessage(message)
                continue
            # if the AR has ReportDryMatter set, get dry_result from form.
            dry_result = ''
            if hasattr(self.context, 'getReportDryMatter') \
               and self.context.getReportDryMatter():
                for k, v in self.request.form['ResultDM'][0].items():
                    if uid == k:
                        dry_result = v
                        break
            results[uid] = result
            interimFields = item_data[uid]
            if len(interimFields) > 0:
                hasInterims[uid] = True
            else:
                hasInterims[uid] = False
            retested = 'retested' in form and uid in form['retested']
            remarks = form.get('Remarks', [{}, ])[0].get(uid, '')
            # Don't save uneccessary things
            # https://github.com/bikalabs/Bika-LIMS/issues/766:
            #    Somehow, using analysis.edit() fails silently when
            #    logged in as Analyst.
            if analysis.getInterimFields() != interimFields or \
               analysis.getRetested() != retested or \
               analysis.getRemarks() != remarks:
                analysis.setInterimFields(interimFields)
                analysis.setRetested(retested)
                analysis.setRemarks(remarks)
            # save results separately, otherwise capture date is rewritten
            if analysis.getResult() != result or \
               analysis.getResultDM() != dry_result:
                analysis.setResultDM(dry_result)
                analysis.setResult(result)
        methods = self.request.form.get('Method', [{}])[0]
        instruments = self.request.form.get('Instrument', [{}])[0]
        analysts = self.request.form.get('Analyst', [{}])[0]
        uncertainties = self.request.form.get('Uncertainty', [{}])[0]
        dlimits = self.request.form.get('DetectionLimit', [{}])[0]
        # discover which items may be submitted
        submissable = []
        for uid, analysis in selected_analyses.items():
            analysis_active = isActive(analysis)

            # Need to save the instrument?
            if uid in instruments and analysis_active:
                # TODO: Add SetAnalysisInstrument permission
                # allow_setinstrument = sm.checkPermission(SetAnalysisInstrument)
                allow_setinstrument = True
                # ---8<-----
                if allow_setinstrument is True:
                    # The current analysis allows the instrument regards
                    # to its analysis service and method?
                    if (instruments[uid]==''):
                        previnstr = analysis.getInstrument()
                        if previnstr:
                            previnstr.removeAnalysis(analysis)
                        analysis.setInstrument(None)
                    elif analysis.isInstrumentAllowed(instruments[uid]):
                        previnstr = analysis.getInstrument()
                        if previnstr:
                            previnstr.removeAnalysis(analysis)
                        analysis.setInstrument(instruments[uid])
                        instrument = analysis.getInstrument()
                        instrument.addAnalysis(analysis)

            # Need to save the method?
            if uid in methods and analysis_active:
                # TODO: Add SetAnalysisMethod permission
                # allow_setmethod = sm.checkPermission(SetAnalysisMethod)
                allow_setmethod = True
                # ---8<-----
                if allow_setmethod is True and analysis.isMethodAllowed(methods[uid]):
                    analysis.setMethod(methods[uid])

            # Need to save the analyst?
            if uid in analysts and analysis_active:
                analysis.setAnalyst(analysts[uid])

            # Need to save the uncertainty?
            if uid in uncertainties and analysis_active:
                analysis.setUncertainty(uncertainties[uid])

            # Need to save the detection limit?
            if analysis_active:
                analysis.setDetectionLimitOperand(dlimits.get(uid, None))

            if uid not in results or not results[uid]:
                continue
            can_submit = True
            # guard_submit does a lot of the same stuff, too.
            # the code there has also been commented.
            # we must find a better way to allow dependencies to control
            # this process.
            # for dependency in analysis.getDependencies():
            #     dep_state = workflow.getInfoFor(dependency, 'review_state')
            #     if hasInterims[uid]:
            #         if dep_state in ('to_be_sampled', 'to_be_preserved',
            #                          'sample_due', 'sample_received',
            #                          'attachment_due', 'to_be_verified',):
            #             can_submit = False
            #             break
            #     else:
            #         if dep_state in ('to_be_sampled', 'to_be_preserved',
            #                          'sample_due', 'sample_received',):
            #             can_submit = False
            #             break
            if can_submit and analysis not in submissable:
                submissable.append(analysis)
        # and then submit them.
        for analysis in submissable:
            doActionFor(analysis, 'submit')

        # LIMS-2366: Finally, when we are done processing all applicable
        # analyses, we must attempt to initiate the submit transition on the
        # AR itself. This is for the case where "general retraction" has been
        # done, or where the last "received" analysis has been removed, and
        # the AR is in state "received" while there are no "received" analyses
        # left to trigger the parent transition.
        if self.context.portal_type == 'Sample':
            ar = self.context.getAnalysisRequests()[0]
        elif self.context.portal_type == 'Analysis':
            ar = self.context.aq_parent
        else:
            ar = self.context
        doActionFor(ar, 'submit')

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')
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
        action, came_from = WorkflowAction._get_form_workflow_action(self)
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

    def workflow_action_retract_ar(self):

        # AR should be retracted
        # Can't transition inactive ARs
        if not api.is_active(self.context):
            message = _('Item is inactive.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(self.context.absolute_url())
            return

        # 1. Copies the AR linking the original one and viceversa
        ar = self.context
        newar = self.cloneAR(ar)

        # 2. The old AR gets a status of 'invalid'
        api.do_transition_for(ar, 'retract_ar')

        # 3. The new AR copy opens in status 'to be verified'
        changeWorkflowState(newar, 'bika_ar_workflow', 'to_be_verified')

        # 4. The system immediately alerts the client contacts who ordered
        # the results, per email and SMS, that a possible mistake has been
        # picked up and is under investigation.
        # A much possible information is provided in the email, linking
        # to the AR online.
        bika_setup = api.get_bika_setup()
        if bika_setup.getNotifyOnARRetract():
            self.notify_ar_retract(ar, newar)

        message = _('${items} invalidated.',
                    mapping={'items': ar.getId()})
        self.context.plone_utils.addPortalMessage(message, 'warning')
        self.request.response.redirect(newar.absolute_url())

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

    def cloneAR(self, ar):
        newar = _createObjectByType("AnalysisRequest", ar.aq_parent, tmpID())
        newar.setSample(ar.getSample())
        ignore_fieldnames = ['Analyses', 'DatePublished', 'DatePublishedViewer',
                             'ParentAnalysisRequest', 'ChildAnaysisRequest',
                             'Digest', 'Sample']
        copy_field_values(ar, newar, ignore_fieldnames=ignore_fieldnames)

        # Set the results for each AR analysis
        ans = ar.getAnalyses(full_objects=True)
        # If a whole AR is retracted and contains retracted Analyses, these
        # retracted analyses won't be created/shown in the new AR
        workflow = getToolByName(self, "portal_workflow")
        analyses = [x for x in ans
                if workflow.getInfoFor(x, "review_state") not in ("retracted")]
        for an in analyses:
            if hasattr(an, 'IsReflexAnalysis') and an.IsReflexAnalysis:
                # We don't want reflex analyses to be copied
                continue
            try:
                nan = _createObjectByType("Analysis", newar, an.getKeyword())
            except Exception as e:
                from bika.lims import logger
                logger.warn('Cannot create analysis %s inside %s (%s)'%
                            an.getAnalysisService().Title(), newar, e)
                continue
            # Make a copy
            ignore_fieldnames = ['Verificators', 'DataAnalysisPublished']
            copy_field_values(an, nan, ignore_fieldnames=ignore_fieldnames)
            nan.unmarkCreationFlag()
            zope.event.notify(ObjectInitializedEvent(nan))
            changeWorkflowState(nan, 'bika_analysis_workflow',
                                'to_be_verified')
            nan.reindexObject()

        newar.reindexObject()
        newar.aq_parent.reindexObject()
        renameAfterCreation(newar)

        if hasattr(ar, 'setChildAnalysisRequest'):
            ar.setChildAnalysisRequest(newar)
        newar.setParentAnalysisRequest(ar)
        return newar

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
