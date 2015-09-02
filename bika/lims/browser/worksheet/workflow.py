# coding=utf-8
from AccessControl import getSecurityManager
from bika.lims import bikaMessageFactory as _
from bika.lims import PMF
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.referenceanalysis import AnalysesRetractedListReport
from bika.lims.permissions import EditResults, EditWorksheet, ManageWorksheets
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
from bika.lims.utils import isActive
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.component import adapts
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.interface import implements
from Products.CMFPlone.i18nl10n import ulocalized_time

import plone
import plone.protect
import json


class WorksheetFolderWorkflowAction(WorkflowAction):
    """ Workflow actions taken in the WorksheetFolder
        This function is called to do the workflow actions
        that apply to worksheets in the WorksheetFolder
    """
    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
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
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
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

            selected_analyses = WorkflowAction._get_selected_items(self)
            selected_analysis_uids = selected_analyses.keys()

            if selected_analyses:
                for uid in selected_analysis_uids:
                    analysis = rc.lookupObject(uid)
                    # Double-check the state first
                    if (workflow.getInfoFor(analysis, 'worksheetanalysis_review_state') == 'unassigned'
                    and workflow.getInfoFor(analysis, 'review_state') == 'sample_received'
                    and workflow.getInfoFor(analysis, 'cancellation_state') == 'active'):
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
                                                came_from='edit')
        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)

    def submit(self):
        """ Saves the form
        """

        form = self.request.form
        remarks = form.get('Remarks', [{}])[0]
        results = form.get('Result',[{}])[0]
        retested = form.get('retested', {})
        methods = form.get('Method', [{}])[0]
        instruments = form.get('Instrument', [{}])[0]
        analysts = self.request.form.get('Analyst', [{}])[0]
        uncertainties = self.request.form.get('Uncertainty', [{}])[0]
        dlimits = self.request.form.get('DetectionLimit', [{}])[0]
        selected = WorkflowAction._get_selected_items(self)
        workflow = getToolByName(self.context, 'portal_workflow')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        sm = getSecurityManager()

        hasInterims = {}
        # XXX combine data from multiple bika listing tables.
        item_data = {}
        if 'item_data' in form:
            if type(form['item_data']) == list:
                for i_d in form['item_data']:
                    for i, d in json.loads(i_d).items():
                        item_data[i] = d
            else:
                item_data = json.loads(form['item_data'])

        # Iterate for each selected analysis and save its data as needed
        for uid, analysis in selected.items():

            allow_edit = sm.checkPermission(EditResults, analysis)
            analysis_active = isActive(analysis)

            # Need to save remarks?
            if uid in remarks and allow_edit and analysis_active:
                analysis.setRemarks(remarks[uid])

            # Retested?
            if uid in retested and allow_edit and analysis_active:
                analysis.setRetested(retested[uid])

            # Need to save the instrument?
            if uid in instruments and analysis_active:
                # TODO: Add SetAnalysisInstrument permission
                # allow_setinstrument = sm.checkPermission(SetAnalysisInstrument)
                allow_setinstrument = True
                # ---8<-----
                if allow_setinstrument == True:
                    # The current analysis allows the instrument regards
                    # to its analysis service and method?
                    if (instruments[uid]==''):
                        previnstr = analysis.getInstrument()
                        if previnstr:
                            previnstr.removeAnalysis(analysis)
                        analysis.setInstrument(None);
                    elif analysis.isInstrumentAllowed(instruments[uid]):
                        previnstr = analysis.getInstrument()
                        if previnstr:
                            previnstr.removeAnalysis(analysis)
                        analysis.setInstrument(instruments[uid])
                        instrument = analysis.getInstrument()
                        instrument.addAnalysis(analysis)
                        if analysis.portal_type == 'ReferenceAnalysis':
                            instrument.setDisposeUntilNextCalibrationTest(False)

            # Need to save the method?
            if uid in methods and analysis_active:
                # TODO: Add SetAnalysisMethod permission
                # allow_setmethod = sm.checkPermission(SetAnalysisMethod)
                allow_setmethod = True
                # ---8<-----
                if allow_setmethod == True and analysis.isMethodAllowed(methods[uid]):
                    analysis.setMethod(methods[uid])

            # Need to save the analyst?
            if uid in analysts and analysis_active:
                analysis.setAnalyst(analysts[uid]);

            # Need to save the uncertainty?
            if uid in uncertainties and analysis_active:
                analysis.setUncertainty(uncertainties[uid])

            # Need to save the detection limit?
            if analysis_active and uid in dlimits and dlimits[uid]:
                analysis.setDetectionLimitOperand(dlimits[uid])

            # Need to save results?
            if uid in results and results[uid] and allow_edit \
                and analysis_active:
                interims = item_data.get(uid, [])
                analysis.setInterimFields(interims)
                analysis.setResult(results[uid])
                analysis.reindexObject()

                can_submit = True
                deps = analysis.getDependencies() \
                        if hasattr(analysis, 'getDependencies') else []
                for dependency in deps:
                    if workflow.getInfoFor(dependency, 'review_state') in \
                       ('to_be_sampled', 'to_be_preserved',
                        'sample_due', 'sample_received'):
                        can_submit = False
                        break
                if can_submit:
                    # doActionFor transitions the analysis to verif pending,
                    # so must only be done when results are submitted.
                    doActionFor(analysis, 'submit')

        # Maybe some analyses need to be retracted due to a QC failure
        # Done here because don't know if the last selected analysis is
        # a valid QC for the instrument used in previous analyses.
        # If we add this logic in subscribers.analyses, there's the
        # possibility to retract analyses before the QC being reached.
        self.retractInvalidAnalyses()

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.destination_url = self.request.get_header("referer",
                               self.context.absolute_url())
        self.request.response.redirect(self.destination_url)

    def retractInvalidAnalyses(self):
        """ Retract the analyses with validation pending status for which
            the instrument used failed a QC Test.
        """
        toretract = {}
        instruments = {}
        refs = []
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        selected = WorkflowAction._get_selected_items(self)
        for uid in selected.iterkeys():
            # We need to do this instead of using the dict values
            # directly because all these analyses have been saved before
            # and don't know if they already had an instrument assigned
            an = rc.lookupObject(uid)
            if an.portal_type == 'ReferenceAnalysis':
                refs.append(an)
                instrument = an.getInstrument()
                if instrument and instrument.UID() not in instruments:
                    instruments[instrument.UID()] = instrument

        for instr in instruments.itervalues():
            analyses = instr.getAnalysesToRetract()
            for a in analyses:
                if a.UID() not in toretract:
                    toretract[a.UID] = a

        retracted = []
        for analysis in toretract.itervalues():
            try:
                # add a remark to this analysis
                failedtxt = ulocalized_time(DateTime(), long_format=0)
                failedtxt = '%s: %s' % (failedtxt, _("Instrument failed reference test"))
                analysis.setRemarks(failedtxt)

                # retract the analysis
                doActionFor(analysis, 'retract')
                retracted.append(analysis)
            except:
                # Already retracted as a dependant from a previous one?
                pass

        if len(retracted) > 0:
            # Create the Retracted Analyses List
            rep = AnalysesRetractedListReport(self.context,
                                               self.request,
                                               self.portal_url,
                                               'Retracted analyses',
                                               retracted)

            # Attach the pdf to the ReferenceAnalysis (accessible
            # from Instrument's Internal Calibration Tests list
            pdf = rep.toPdf()
            for ref in refs:
                ref.setRetractedAnalysesPdfReport(pdf)

            # Send the email
            try:
                rep.sendEmail()
            except:
                pass

            # TODO: mostra una finestra amb els resultats publicats d'AS
            # que han utilitzat l'instrument des de la seva última
            # calibració vàlida, amb els emails, telèfons dels
            # contactes associats per a una intervenció manual
            pass
