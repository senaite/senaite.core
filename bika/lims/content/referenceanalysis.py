# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import logger, deprecated
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME, STD_TYPES
from bika.lims.content.abstractanalysis import AbstractAnalysis
from bika.lims.content.abstractanalysis import schema
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.permissions import Verify as VerifyPermission
from bika.lims.subscribers import skip
from bika.lims.utils.analysis import get_significant_digits
from bika.lims.workflow import doActionFor
from plone.app.blob.field import BlobField
from zope.interface import implements
from plone.api.user import has_permission

schema = schema.copy() + Schema((
    StringField(
        'ReferenceType',
        vocabulary=STD_TYPES,
    ),
    BlobField(
        'RetractedAnalysesPdfReport',
    ),
    StringField(
        'ReferenceAnalysesGroupID',
    )
))


class ReferenceAnalysis(AbstractAnalysis):
    implements(IReferenceAnalysis)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def getSupplier(self):
        """ Returns the Supplier of the ReferenceSample this ReferenceAnalysis
        refers to
        """
        return self.getSample().aq_parent

    def getSupplierUID(self):
        return self.getSupplier().UID()

    def getSample(self):
        """ Returns the ReferenceSample this ReferenceAnalysis refers to
        Delegates to self.aq_parent
        """
        return self.aq_parent

    @security.public
    def setResult(self, value):
        # Always update ResultCapture date when this field is modified
        self.setResultCaptureDate(DateTime())
        val = str(value).strip()
        self.getField('Result').set(self, val)

    def getExpiryDate(self):
        """It is used as a metacolumn.
        Returns the expiration date from the reference sample.
        """
        return self.getSample().getExpiryDate()

    def getReferenceResults(self):
        """
        It is used as metacolumn
        """
        return self.getSample().getReferenceResults()

    def getDependencies(self):
        """It doesn't make sense for a ReferenceAnalysis to use
        dependencies, since them are only used in calculations for
        routine analyses
        """
        return []

    @security.public
    @deprecated('05-2017. Use after_submit_transition_event instead')
    def workflow_script_submit(self):
        self.after_submit_transition_event()

    @security.public
    def after_submit_transition_event(self):
        """Method triggered after a 'submit' transition for the current
        ReferenceAnalysis is performed.
        By default, the "submit" action for transitions the RefAnalysis to the
        "attachment_due" state. If attachment is not required, the Reference
        Analysis is transitioned to 'to_be_verified' state (via 'attach').
        If all the analyses that belong to the same worksheet are in a suitable
        state, the 'submit' transition to the worksheet is triggered too.
        This function is called automatically by
        bika.lims.workflow.AfterTransitionEventHandler
        """
        # By default, the 'submit' action transitions the ReferenceAnalysis to
        # the 'attachment_due'. Since doActionFor already checks for the guards
        # in this case (guard_attach_transition), try always the transition to
        # 'to_be_verified' via 'attach' action
        # doActionFor will check the
        doActionFor(self, attach)

        # Delegate the transition of Worksheet to base class AbstractAnalysis
        super(AbstractRoutineAnalysis, self).after_submit_transition_event()

    def workflow_script_attach(self):
        if skip(self, "attach"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        # If all analyses on the worksheet have been attached,
        # then attach the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        ws_state = workflow.getInfoFor(ws, 'review_state')
        if ws_state == 'attachment_due' and not skip(ws, "attach", peek=True):
            can_attach = True
            for a in ws.getAnalyses():
                if workflow.getInfoFor(a, 'review_state') in \
                        ('sample_due', 'sample_received', 'attachment_due',
                         'assigned',):
                    can_attach = False
                    break
            if can_attach:
                workflow.doActionFor(ws, 'attach')
        self.reindexObject()

    def workflow_script_retract(self):
        if skip(self, "retract"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        # Escalate action to the Worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        if not skip(ws, "retract", peek=True):
            if workflow.getInfoFor(ws, 'review_state') == 'open':
                skip(ws, "retract")
            else:
                if "retract all analyses" \
                        not in self.REQUEST['workflow_skiplist']:
                    self.REQUEST["workflow_skiplist"].append(
                        "retract all analyses")
                workflow.doActionFor(ws, 'retract')
        self.reindexObject()

    def workflow_script_verify(self):
        if skip(self, "verify"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        # If all other analyses on the worksheet are verified,
        # then verify the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        if ws and len(ws) > 0:
            ws = ws[0]
            ws_state = workflow.getInfoFor(ws, 'review_state')
            if ws_state == 'to_be_verified' and not skip(ws, "verify",
                                                         peek=True):
                all_verified = True
                for a in ws.getAnalyses():
                    if workflow.getInfoFor(a, 'review_state') in \
                            ('sample_due', 'sample_received', 'attachment_due',
                             'to_be_verified', 'assigned'):
                        all_verified = False
                        break
                if all_verified:
                    if "verify all analyses" \
                            not in self.REQUEST['workflow_skiplist']:
                        self.REQUEST["workflow_skiplist"].append(
                            "verify all analyses")
                    workflow.doActionFor(ws, "verify")
        self.reindexObject()

    def workflow_script_assign(self):
        if skip(self, "assign"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        rc = getToolByName(self, REFERENCE_CATALOG)
        if 'context_uid' in self.REQUEST:
            wsUID = self.REQUEST['context_uid']
            ws = rc.lookupObject(wsUID)

            # retract the worksheet to 'open'
            ws_state = workflow.getInfoFor(ws, 'review_state')
            if ws_state != 'open':
                if 'workflow_skiplist' not in self.REQUEST:
                    self.REQUEST['workflow_skiplist'] = [
                        'retract all analyses', ]
                else:
                    self.REQUEST["workflow_skiplist"].append(
                        'retract all analyses')
                workflow.doActionFor(ws, 'retract')
        self.reindexObject()

    def workflow_script_unassign(self):
        if skip(self, "unassign"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        rc = getToolByName(self, REFERENCE_CATALOG)
        wsUID = self.REQUEST['context_uid']
        ws = rc.lookupObject(wsUID)

        # May need to promote the Worksheet's review_state
        #  if all other analyses are at a higher state than this one was.
        # (or maybe retract it if there are no analyses left)
        # Note: duplicates, controls and blanks have 'assigned' as a
        # review_state.
        can_submit = True
        can_attach = True
        can_verify = True
        ws_empty = False

        analyses = ws.getAnalyses()

        # We flag this worksheet as empty if there is ONE UNASSIGNED
        # analysis left: worksheet.removeAnalysis() hasn't removed it from
        # the layout yet at this stage.
        if len(analyses) == 1 \
                and workflow.getInfoFor(analyses[0],
                                        'review_state') == 'unassigned':
            ws_empty = True

        for a in analyses:
            a_state = workflow.getInfoFor(a, 'review_state')
            if a_state in \
                    ('assigned', 'sample_due', 'sample_received',):
                can_submit = False
            else:
                if not ws.getAnalyst():
                    can_submit = False
            if a_state in \
                    ('assigned', 'sample_due', 'sample_received',
                     'attachment_due',):
                can_attach = False
            if a_state in \
                    ('assigned', 'sample_due', 'sample_received',
                     'attachment_due', 'to_be_verified',):
                can_verify = False

        if not ws_empty:
            # Note: WS adds itself to the skiplist so we have to take it off
            # again
            #       to allow multiple promotions (maybe by more than one self).
            if can_submit and workflow.getInfoFor(ws, 'review_state') == 'open':
                workflow.doActionFor(ws, 'submit')
                skip(ws, 'submit', unskip=True)
            if can_attach and workflow.getInfoFor(ws,
                                                  'review_state') == \
                    'attachment_due':
                workflow.doActionFor(ws, 'attach')
                skip(ws, 'attach', unskip=True)
            if can_verify and workflow.getInfoFor(ws,
                                                  'review_state') == \
                    'to_be_verified':
                self.REQUEST["workflow_skiplist"].append('verify all analyses')
                workflow.doActionFor(ws, 'verify')
                skip(ws, 'verify', unskip=True)
        else:
            if workflow.getInfoFor(ws, 'review_state') != 'open':
                workflow.doActionFor(ws, 'retract')
                skip(ws, 'retract', unskip=True)
        self.reindexObject()


registerType(ReferenceAnalysis, PROJECTNAME)
