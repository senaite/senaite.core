# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json
from operator import attrgetter

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time
from bika.lims import api
from bika.lims import PMF
from bika.lims import bikaMessageFactory as _
from bika.lims.api.analysis import is_out_of_range
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.referenceanalysis import AnalysesRetractedListReport
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.permissions import ManageWorksheets
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
from bika.lims.workflow import in_state
from DateTime import DateTime
from plone.protect import CheckAuthenticator


class WorksheetFolderWorkflowAction(WorkflowAction):
    """ Workflow actions taken in the WorksheetFolder
        This function is called to do the workflow actions
        that apply to worksheets in the WorksheetFolder
    """
    def __call__(self):
        form = self.request.form
        CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        action, came_from = WorkflowAction._get_form_workflow_action(self)

        if action == 'reassign':
            mtool = getToolByName(self.context, 'portal_membership')
            if not mtool.checkPermission(ManageWorksheets, self.context):

                # Redirect to WS list
                msg = _('You do not have sufficient privileges to '
                        'manage worksheets.')
                self.context.plone_utils.addPortalMessage(msg, 'warning')
                portal = getToolByName(self.context, 'portal_url').getPortalObject()
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
                    if workflow.getInfoFor(worksheet, 'review_state') == 'open':
                        worksheet.setAnalyst(form['Analyst'][0][uid])
                        worksheet.reindexObject(idxs=['getAnalyst'])
                        changes = True

                if changes:
                    message = PMF('Changes saved.')
                    self.context.plone_utils.addPortalMessage(message, 'info')

            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)
        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)



class WorksheetWorkflowAction(WorkflowAction):
    """ Workflow actions taken in Worksheets
        This function is called to do the worflow actions
        that apply to analyses in worksheets
    """
    def __call__(self):
        form = self.request.form
        CheckAuthenticator(form)
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        action, came_from = WorkflowAction._get_form_workflow_action(self)

        if action == 'submit':
            # Submit the form. Saves the results, methods, etc.
            self.submit()

        ## assign
        elif action == 'assign':
            if not self.context.checkUserManage():
                self.request.response.redirect(self.context.absolute_url())
                return

            analysis_uids = form.get("uids", [])
            if analysis_uids:
                # We retrieve the analyses from the database sorted by AR ID
                # ascending, so the positions of the ARs inside the WS are
                # consistent with the order of the ARs
                catalog = api.get_tool(CATALOG_ANALYSIS_LISTING)
                brains = catalog({'UID': analysis_uids,
                                  'sort_on': 'getRequestID'})

                # Now, we need the analyses within a request ID to be sorted by
                # sortkey (sortable_title index), so it will appear in the same
                # order as they appear in Analyses list from AR view
                curr_arid = None
                curr_brains = []
                sorted_brains = []
                for brain in brains:
                    arid = brain.getRequestID
                    if curr_arid != arid:
                        # Sort the brains we've collected until now, that belong to
                        # the same Analysis Request
                        curr_brains.sort(key=attrgetter('getPrioritySortkey'))
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
                for brain in sorted_brains:
                    analysis = brain.getObject()
                    self.context.addAnalysis(analysis)

            self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)
        ## unassign
        elif action == 'unassign':
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

            message = PMF("Changes saved.")
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)
        ## verify
        elif action == 'verify':
            # default bika_listing.py/WorkflowAction, but then go to view screen.
            self.destination_url = self.context.absolute_url()
            return self.workflow_action_default(action='verify',
                                                came_from=came_from)
        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)

    def submit(self):
        """ Saves the form
        """
        uids = self.get_selected_uids()
        if not uids:
            return

        form = self.request.form
        remarks = form.get('Remarks', [{}])[0]
        results = form.get('Result',[{}])[0]
        retested = form.get('retested', {})
        methods = form.get('Method', [{}])[0]
        instruments = form.get('Instrument', [{}])[0]
        analysts = self.request.form.get('Analyst', [{}])[0]
        uncertainties = self.request.form.get('Uncertainty', [{}])[0]
        dlimits = self.request.form.get('DetectionLimit', [{}])[0]

        # XXX combine data from multiple bika listing tables.
        # TODO: What's this for? I am lost here...
        item_data = {}
        if 'item_data' in form:
            if type(form['item_data']) == list:
                for i_d in form['item_data']:
                    for i, d in json.loads(i_d).items():
                        item_data[i] = d
            else:
                item_data = json.loads(form['item_data'])

        # Store Analysis Requests that need to be reindexed
        ar_uids_to_reindex = set()

        # Store invalid instruments-ref.analyses
        invalid_instrument_refs = dict()

        # We manually query by all analyses uids at once here instead of using
        # _get_selected_items from the base class, cause that function fetches
        # the objects by uid, but sequentially one by one
        worksheet_uid = api.get_uid(self.context)
        query = dict(getWorksheetUID=worksheet_uid, UID=uids,
                     cancellation_state='active')
        for brain in api.search(query, CATALOG_ANALYSIS_LISTING):
            uid = api.get_uid(brain)
            analysis = api.get_object(brain)

            # Need to save remarks?
            if uid in remarks:
                analysis.setRemarks(remarks[uid])

            # Retested?
            if uid in retested:
                analysis.setRetested(retested[uid])

            # Need to save the instrument?
            if uid in instruments:
                instrument = instruments[uid] or None
                analysis.setInstrument(instrument)
                if instrument and IReferenceAnalysis.providedBy(analysis):
                    if is_out_of_range(analysis):
                        # This reference analysis is out of range, so we have
                        # to retract all analyses assigned to this same
                        # instrument that are awaiting for verification
                        if uid not in invalid_instrument_refs:
                            invalid_instrument_refs[uid]=set()
                        invalid_instrument_refs[uid].add(analysis)
                    else:
                        # The reference result is valid, so make the instrument
                        # available again for further analyses
                        instrument.setDisposeUntilNextCalibrationTest(False)

            # Need to save the method?
            if uid in methods:
                method = methods[uid] or None
                analysis.setMethod(method)

            # Need to save the analyst?
            if uid in analysts:
                analysis.setAnalyst(analysts[uid])

            # Need to save the uncertainty?
            if uid in uncertainties:
                analysis.setUncertainty(uncertainties[uid])

            # Need to save the detection limit?
            if uid in dlimits and dlimits[uid]:
                analysis.setDetectionLimitOperand(dlimits[uid])

            # Need to save results?
            submitted = False
            if uid in results and results[uid]:
                interims = item_data.get(uid, [])
                analysis.setInterimFields(interims)
                analysis.setResult(results[uid])

                # Can the analysis be submitted?
                # An analysis can only be submitted if all its dependencies
                # are valid and have been submitted already
                can_submit = True
                invalid_states = ['to_be_sampled', 'to_be_preserved',
                                  'sample_due', 'sample_received']
                for dependency in analysis.getDependencies():
                    if in_state(dependency, invalid_states):
                        can_submit = False
                        break
                if can_submit:
                    # doActionFor transitions the analysis to verif pending,
                    # so must only be done when results are submitted.
                    doActionFor(analysis, 'submit')
                    submitted = True
                    if IRequestAnalysis.providedBy(analysis):
                        # Store the AR uids to be reindexed later.
                        ar_uids_to_reindex.add(brain.getParentUID)

            if not submitted:
                # Analysis has not been submitted, so we need to reindex the
                # object manually, to update catalog's metadata.
                analysis.reindexObject()

        # Reindex the Analysis Requests for which at least one Analysis has
        # been submitted. We do this here because one AR can contain multiple
        # Analyses, so better to just reindex the AR once instead of each time.
        # AR Catalog contains some metadata that that rely on the Analyses an
        # Analysis Request contains.
        if ar_uids_to_reindex:
            query = dict(UID=ar_uids_to_reindex)
            for ar_brain in api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING):
                if ar_brain.review_state == 'to_be_verified':
                    continue
                ar = api.get_object(ar_brain)
                ar.reindexObject(idxs='assigned_state')

        # If a reference analysis with an out-of-range result and instrument
        # assigned has been submitted, retract then routine analyses that are
        # awaiting for verification and with same instrument associated
        retracted = list()
        for invalid_instrument_uid in invalid_instrument_refs.keys():
            query = dict(getInstrumentUID=invalid_instrument_uid,
                         portal_type=['Analysis', 'DuplicateAnalysis'],
                         review_state='to_be_verified',
                         cancellation_state='active',)
            brains = api.search(query, CATALOG_ANALYSIS_LISTING)
            for brain in brains:
                analysis = api.get_object(brain)
                failed_msg = '{0}: {1}'.format(
                    ulocalized_time(DateTime(), long_format=1),
                    _("Instrument failed reference test"))
                an_remarks = analysis.getRemarks()
                analysis.setRemarks('. '.join([an_remarks, failed_msg]))
                doActionFor(analysis, 'retract')
                retracted.append(analysis)

        # If some analyses have been retracted because instrument failed a
        # reference test, then generate a pdf report
        if retracted:
            # Create the Retracted Analyses List
            report = AnalysesRetractedListReport(self.context, self.request,
                                              self.portal_url,
                                              'Retracted analyses', retracted)

            # Attach the pdf to all ReferenceAnalysis that failed (accessible
            # from Instrument's Internal Calibration Tests list
            pdf = report.toPdf()
            for ref in invalid_instrument_refs.values():
                ref.setRetractedAnalysesPdfReport(pdf)

            # Send the email
            try:
                report.sendEmail()
            except:
                pass

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.destination_url = self.request.get_header("referer",
                               self.context.absolute_url())
        self.request.response.redirect(self.destination_url)
