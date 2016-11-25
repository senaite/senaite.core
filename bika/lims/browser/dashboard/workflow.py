# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import getSecurityManager
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t, dicts_to_dict, format_supsub
from bika.lims.utils.analysis import format_uncertainty
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.config import QCANALYSIS_TYPES
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.permissions import *
from bika.lims.utils import isActive
from bika.lims.utils import getUsers
from bika.lims.utils import to_utf8
from bika.lims.utils import formatDecimalMark
from bika.lims.browser.bika_listing import WorkflowAction
from DateTime import DateTime
from operator import itemgetter
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.utils.analysis import format_numeric_result
from zope.interface import implements
from zope.interface import Interface
from zope.component import getAdapters

import json


class AggregatedAnalysesWorkflowAction(WorkflowAction):
    """ Workflow actions taken in Worksheets
        This function is called to do the worflow actions
        that apply to analyses in worksheets
    """

    def workflow_action_submit(self):
        """ Saves the form
        """
        import pdb; pdb.set_trace()
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

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        if self.destination_url == "":
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
        self.request.response.redirect(self.destination_url)
