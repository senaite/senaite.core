# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import Schema, registerType
from Products.Archetypes.public import StringField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME
from bika.lims.content.abstractroutineanalysis import AbstractRoutineAnalysis
from bika.lims.content.abstractroutineanalysis import schema
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.subscribers import skip
from plone.api.portal import get_tool
from zope.interface import implements

# A reference back to the original analysis from which this one was duplicated.
Analysis = UIDReferenceField(
    'Analysis',
    required=1,
    allowed_types=('Analysis', 'ReferenceAnalysis'),
)

# TODO Analysis - Duplicates shouldn't have this attribute, only ReferenceAns
ReferenceAnalysesGroupID = StringField(
    'ReferenceAnalysesGroupID',
)

schema = schema.copy() + Schema((
    Analysis,
    ReferenceAnalysesGroupID,
))


class DuplicateAnalysis(AbstractRoutineAnalysis):
    implements(IDuplicateAnalysis)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    @security.public
    def getRequest(self):
        """Returns the Analysis Request of the original analysis.
        """
        analysis = self.getAnalysis()
        if analysis:
            return analysis.getRequest()

    @security.public
    def getAnalysisPortalType(self):
        """This returns the portal_type of the original analysis.
        """
        analysis = self.getAnalysis()
        if analysis:
            return analysis.portal_type

    @security.public
    def getSample(self):
        """Returns the Sample of the original analysis.
        """
        analysis = self.getAnalysis()
        if analysis:
            return analysis.getSample()

    @security.public
    def getWorksheet(self):
        return self.aq_parent

    @security.public
    def getSiblings(self):
        """Returns the list of duplicate analyses that share the same Request
        and are included in the same Worksheet as the current. The current
        duplicate is excluded from the list
        """
        worksheet = self.getWorksheet()
        requestuid = self.getRequestUID()
        if not requestuid or not worksheet:
            return []
        analyses = worksheet.getAnalyses()
        siblings = [an for an in analyses if an.getRequestUID() == requestuid]
        siblings = [an for an in analyses if an.UID() != self.UID()]
        return siblings

    @security.public
    def workflow_script_attach(self):
        if skip(self, "attach"):
            return
        workflow = get_tool('portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        # If all analyses on the worksheet have been attached,
        # then attach the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        ws_state = workflow.getInfoFor(ws, 'review_state')
        if ws_state == 'attachment_due' and not skip(ws, "attach", peek=True):
            can_attach = True
            for a in ws.getAnalyses():
                state = workflow.getInfoFor(a, 'review_state')
                if state in ('to_be_sampled', 'to_be_preserved', 'sample_due',
                             'sample_received', 'attachment_due', 'assigned'):
                    can_attach = False
                    break
            if can_attach:
                workflow.doActionFor(ws, 'attach')

    @security.public
    def workflow_script_retract(self):
        if skip(self, "retract"):
            return
        workflow = get_tool('portal_workflow')
        # Escalate action to the Worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        if skip(ws, "retract", peek=True):
            if workflow.getInfoFor(ws, 'review_state') == 'open':
                skip(ws, "retract")
            else:
                if "retract all analyses" \
                        not in self.REQUEST['workflow_skiplist']:
                    self.REQUEST["workflow_skiplist"].append(
                        "retract all analyses")
                workflow.doActionFor(ws, 'retract')
        self.reindexObject()

    @security.public
    def workflow_script_verify(self):
        if skip(self, "verify"):
            return
        workflow = get_tool('portal_workflow')
        # If all other analyses on the worksheet are verified,
        # then verify the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        ws_state = workflow.getInfoFor(ws, 'review_state')
        if ws_state == 'to_be_verified' and not skip(ws, "verify", peek=True):
            all_verified = True
            for a in ws.getAnalyses():
                state = workflow.getInfoFor(a, 'review_state')
                if state in ('to_be_sampled', 'to_be_preserved', 'sample_due',
                             'sample_received', 'attachment_due', 'assigned',
                             'to_be_verified'):
                    all_verified = False
                    break
            if all_verified:
                if "verify all analyses" \
                        not in self.REQUEST['workflow_skiplist']:
                    self.REQUEST["workflow_skiplist"].append(
                        "verify all analyses")
                workflow.doActionFor(ws, "verify")
        self.reindexObject()

    @security.public
    def workflow_script_assign(self):
        if skip(self, "assign"):
            return
        workflow = get_tool('portal_workflow')
        rc = get_tool("reference_catalog")
        wsUID = self.REQUEST['context_uid']
        ws = rc.lookupObject(wsUID)
        # retract the worksheet to 'open'
        ws_state = workflow.getInfoFor(ws, 'review_state')
        if ws_state != 'open':
            if 'workflow_skiplist' not in self.REQUEST:
                self.REQUEST['workflow_skiplist'] = ['retract all analyses', ]
            else:
                self.REQUEST["workflow_skiplist"].append('retract all analyses')
            workflow.doActionFor(ws, 'retract')
        self.reindexObject()

    @security.public
    def workflow_script_unassign(self):
        if skip(self, "unassign"):
            return
        workflow = get_tool('portal_workflow')
        rc = get_tool("reference_catalog")
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
        state = workflow.getInfoFor(analyses[0], 'review_state')
        if len(analyses) == 1 and state == 'unassigned':
            ws_empty = True
        for a in analyses:
            ws_empty = False
            a_state = workflow.getInfoFor(a, 'review_state')
            if a_state in ('assigned', 'sample_due', 'sample_received'):
                can_submit = False
            else:
                if not ws.getAnalyst():
                    can_submit = False
            if a_state in ('assigned', 'sample_due', 'sample_received',
                           'attachment_due'):
                can_attach = False
            if a_state in ('assigned', 'sample_due', 'sample_received',
                           'attachment_due', 'to_be_verified'):
                can_verify = False
        state = workflow.getInfoFor(ws, 'review_state')
        if not ws_empty:
            # Note: WS adds itself to the skiplist so we have to take it off
            # again to allow multiple promotions (maybe by more than one self).
            # There-from come the unskips below.
            if can_submit and state == 'open':
                workflow.doActionFor(ws, 'submit')
                skip(ws, 'submit', unskip=True)
            if can_attach and state == 'attachment_due':
                workflow.doActionFor(ws, 'attach')
                skip(ws, 'attach', unskip=True)
            if can_verify and state == 'to_be_verified':
                self.REQUEST["workflow_skiplist"].append('verify all analyses')
                workflow.doActionFor(ws, 'verify')
                skip(ws, 'verify', unskip=True)
        else:
            if state != 'open':
                workflow.doActionFor(ws, 'retract')
                skip(ws, 'retract', unskip=True)
        self.reindexObject()


registerType(DuplicateAnalysis, PROJECTNAME)
