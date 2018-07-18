# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json

from DateTime import DateTime
from Products.CMFPlone.i18nl10n import ulocalized_time
from bika.lims import PMF
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.api import is_active
from bika.lims.api.analysis import is_out_of_range
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.referenceanalysis import AnalysesRetractedListReport
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog.worksheet_catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.subscribers import doActionFor
from bika.lims.workflow import in_state, isTransitionAllowed


class AnalysesWorkflowAction(WorkflowAction):
    """Workflow actions taken in lists that contains analyses"""

    def workflow_action_submit(self):
        uids = self.get_selected_uids()
        if not uids:
            message = _('No items selected.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(self.context.absolute_url())
            return

        if not is_active(self.context):
            message = _('Item is inactive.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(self.context.absolute_url())
            return

        form = self.request.form
        remarks = form.get('Remarks', [{}])[0]
        results = form.get('Result', [{}])[0]
        retested = form.get('retested', {})
        methods = form.get('Method', [{}])[0]
        instruments = form.get('Instrument', [{}])[0]
        analysts = self.request.form.get('Analyst', [{}])[0]
        uncertainties = self.request.form.get('Uncertainty', [{}])[0]
        dlimits = self.request.form.get('DetectionLimit', [{}])[0]

        # XXX combine data from multiple bika listing tables.
        # TODO: Is this necessary?
        item_data = {}
        if 'item_data' in form:
            if type(form['item_data']) == list:
                for i_d in form['item_data']:
                    for i, d in json.loads(i_d).items():
                        item_data[i] = d
            else:
                item_data = json.loads(form['item_data'])

        # Store affected Analysis Requests
        affected_ars = set()

        # Store affected Worksheets
        affected_ws = set()

        # Store invalid instruments-ref.analyses
        invalid_instrument_refs = dict()

        # We manually query by all analyses uids at once here instead of using
        # _get_selected_items from the base class, cause that function fetches
        # the objects by uid, but sequentially one by one
        query = dict(UID=uids)
        for brain in api.search(query, CATALOG_ANALYSIS_LISTING):
            uid = api.get_uid(brain)
            analysis = api.get_object(brain)

            # If not active, do nothing
            if not is_active(brain):
                continue

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
                            invalid_instrument_refs[uid] = set()
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
                        affected_ars.add(brain.getParentUID )

                    if brain.worksheetanalysis_review_state == 'assigned':
                        worksheet_uid = analysis.getWorksheetUID()
                        if worksheet_uid:
                            affected_ws.add(worksheet_uid)

            if not submitted:
                # Analysis has not been submitted, so we need to reindex the
                # object manually, to update catalog's metadata.
                analysis.reindexObject()

        # If a reference analysis with an out-of-range result and instrument
        # assigned has been submitted, retract then routine analyses that are
        # awaiting for verification and with same instrument associated
        retracted = list()
        for invalid_instrument_uid in invalid_instrument_refs.keys():
            query = dict(getInstrumentUID=invalid_instrument_uid,
                         portal_type=['Analysis', 'DuplicateAnalysis'],
                         review_state='to_be_verified',
                         cancellation_state='active', )
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
                                                 'Retracted analyses',
                                                 retracted)

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

        # Finally, when we are done processing all applicable analyses, we must
        # attempt to initiate the submit transition on the ARs and Worksheets
        # the processed analyses belong to.
        # We stick only to affected_ars, and affected_ws

        # Reindex the Analysis Requests for which at least one Analysis has
        # been submitted. We do this here because one AR can contain multiple
        # Analyses, so better to just reindex the AR once instead of each time.
        # AR Catalog contains some metadata that that rely on the Analyses an
        # Analysis Request contains.
        if affected_ars:
            query = dict(UID=list(affected_ars), portal_type="AnalysisRequest")
            for ar_brain in api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING):
                if ar_brain.review_state == 'to_be_verified':
                    continue
                ar = api.get_object(ar_brain)
                if isTransitionAllowed(ar, "submit"):
                    doActionFor(ar, "submit")
                else:
                    ar.reindexObject()

        if affected_ws:
            query = dict(UID=list(affected_ws), portal_type="Worksheet")
            for ws_brain in api.search(query, CATALOG_WORKSHEET_LISTING):
                if ws_brain.review_state == 'to_be_verified':
                    continue
                ws = api.get_object(ws_brain)
                if isTransitionAllowed(ws, "submit"):
                    doActionFor(ws, "submit")

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.destination_url = self.request.get_header("referer",
                                                       self.context.absolute_url())
        self.request.response.redirect(self.destination_url)

