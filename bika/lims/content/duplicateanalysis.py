"""DuplicateAnalysis uses Analysis as it's base.  Until that's fixed there
is some confusion.
"""
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.config import PROJECTNAME
from bika.lims.content.analysis import schema, Analysis
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.subscribers import skip
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


schema = schema.copy() + Schema((
    ReferenceField(
        'Analysis',
        required=1,
        allowed_types=('Analysis',),
        referenceClass=HoldingReference,
        relationship='DuplicateAnalysisAnalysis',
    ),
    InterimFieldsField(
        'InterimFields',
    ),
    StringField(
        'Result',
    ),
    StringField(
        'ResultDM',
    ),
    BooleanField(
        'Retested',
    ),
    ReferenceField(
        'Attachment',
        multiValued=1,
        allowed_types=('Attachment',),
        referenceClass=HoldingReference,
        relationship='DuplicateAnalysisAttachment',
    ),

    StringField(
        'Analyst',
    ),
    ReferenceField(
        'Instrument',
        required=0,
        allowed_types=('Instrument',),
        relationship='AnalysisInstrument',
        referenceClass=HoldingReference,
    ),
    ComputedField(
        'SamplePartition',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getSamplePartition()',
    ),
    ComputedField(
        'ClientOrderNumber',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getClientOrderNumber()',
    ),
    ComputedField(
        'Service',
        expression='context.getAnalysis() and context.getAnalysis().getService() or ""',
    ),
    ComputedField(
        'ServiceUID',
        expression='context.getAnalysis() and context.getAnalysis().getServiceUID()',
    ),
    ComputedField(
        'CategoryUID',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getCategoryUID()',
    ),
    ComputedField(
        'Calculation',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getCalculation()',
    ),
    ComputedField(
        'ReportDryMatter',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getReportDryMatter()',
    ),
    ComputedField(
        'DateReceived',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getDateReceived()',
    ),
    ComputedField(
        'MaxTimeAllowed',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getMaxTimeAllowed()',
    ),
    ComputedField(
        'DueDate',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getDueDate()',
    ),
    ComputedField(
        'Duration',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getDuration()',
    ),
    ComputedField(
        'Earliness',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getEarliness()',
    ),
    ComputedField(
        'ClientUID',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getClientUID()',
    ),
    ComputedField(
        'RequestID',
        expression='context.getAnalysis() and context.getAnalysis().aq_parent.portal_type=="AnalysisRequest" and context.getAnalysis().getRequestID() or ""',
    ),
    ComputedField(
        'PointOfCapture',
        expression='context.getAnalysis() and context.getAnalysis().getPointOfCapture()',
    ),
    StringField(
        'ReferenceAnalysesGroupID',
        widget=StringWidget(
            label=_("ReferenceAnalysesGroupID"),
            visible=False,
        ),
    ),
    ComputedField(
        'Keyword',
        expression="context.getAnalysis().getKeyword()",
    ),
),
)


class DuplicateAnalysis(Analysis):
    implements(IDuplicateAnalysis)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getSample(self):
        analysis = self.getAnalysis()
        # check for getSample access, eg. ReferenceAnalysis
        if hasattr(analysis, 'getSample'):
            return analysis.getSample()
        # traverse to parent for getSample access
        analysis_parent = analysis.aq_parent
        if hasattr(analysis_parent, 'getSample'):
            return analysis_parent.getSample()

    def workflow_script_submit(self):
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        # If all analyses on the worksheet have been submitted,
        # then submit the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        # if the worksheet analyst is not assigned, the worksheet can't  be transitioned.
        if ws.getAnalyst() and not skip(ws, "submit", peek=True):
            all_submitted = True
            for a in ws.getAnalyses():
                if workflow.getInfoFor(a, 'review_state') in \
                   ('to_be_sampled', 'to_be_preserved', 'sample_due',
                    'sample_received', 'assigned',):
                    all_submitted = False
                    break
            if all_submitted:
                workflow.doActionFor(ws, 'submit')
        # If no problem with attachments, do 'attach' action.
        can_attach = True
        if not self.getAttachment():
            service = self.getService()
            if service.getAttachmentOption() == 'r':
                can_attach = False
        if can_attach:
            workflow.doActionFor(self, 'attach')

    def workflow_script_attach(self):
        if skip(self, "attach"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        # If all analyses on the worksheet have been attached,
        # then attach the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        ws_state = workflow.getInfoFor(ws, 'review_state')
        if ws_state == 'attachment_due' and not skip(ws, "attach", peek=True):
            can_attach = True
            for a in ws.getAnalyses():
                if workflow.getInfoFor(a, 'review_state') in \
                   ('to_be_sampled', 'to_be_preserved', 'sample_due',
                    'sample_received', 'attachment_due', 'assigned',):
                    can_attach = False
                    break
            if can_attach:
                workflow.doActionFor(ws, 'attach')

        return

    def workflow_script_retract(self):
        if skip(self, "retract"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        # Escalate action to the Worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        if skip(ws, "retract", peek=True):
            if workflow.getInfoFor(ws, 'review_state') == 'open':
                skip(ws, "retract")
            else:
                if not "retract all analyses" in self.REQUEST['workflow_skiplist']:
                    self.REQUEST["workflow_skiplist"].append("retract all analyses")
                workflow.doActionFor(ws, 'retract')

    def workflow_script_verify(self):
        if skip(self, "verify"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        # If all other analyses on the worksheet are verified,
        # then verify the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        ws_state = workflow.getInfoFor(ws, 'review_state')
        if ws_state == 'to_be_verified' and not skip(ws, "verify", peek=True):
            all_verified = True
            for a in ws.getAnalyses():
                if workflow.getInfoFor(a, 'review_state') in \
                   ('to_be_sampled', 'to_be_preserved', 'sample_due',
                    'sample_received', 'attachment_due', 'to_be_verified', 'assigned'):
                    all_verified = False
                    break
            if all_verified:
                if not "verify all analyses" in self.REQUEST['workflow_skiplist']:
                    self.REQUEST["workflow_skiplist"].append("verify all analyses")
                workflow.doActionFor(ws, "verify")

    def workflow_script_assign(self):
        if skip(self, "assign"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        rc = getToolByName(self, REFERENCE_CATALOG)
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

    def workflow_script_unassign(self):
        if skip(self, "unassign"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        rc = getToolByName(self, REFERENCE_CATALOG)
        wsUID = self.REQUEST['context_uid']
        ws = rc.lookupObject(wsUID)

        # May need to promote the Worksheet's review_state
        #  if all other analyses are at a higher state than this one was.
        # (or maybe retract it if there are no analyses left)
        # Note: duplicates, controls and blanks have 'assigned' as a review_state.
        can_submit = True
        can_attach = True
        can_verify = True
        ws_empty = False
        analyses = ws.getAnalyses()
        # We flag this worksheet as empty if there is ONE UNASSIGNED
        # analysis left: worksheet.removeAnalysis() hasn't removed it from
        # the layout yet at this stage.
        if len(analyses) == 1 \
           and workflow.getInfoFor(analyses[0], 'review_state') == 'unassigned':
            ws_empty = True
        for a in analyses:
            ws_empty = False
            a_state = workflow.getInfoFor(a, 'review_state')
            if a_state in \
               ('assigned', 'sample_due', 'sample_received',):
                can_submit = False
            else:
                if not ws.getAnalyst():
                    can_submit = False
            if a_state in \
               ('assigned', 'sample_due', 'sample_received', 'attachment_due',):
                can_attach = False
            if a_state in \
               ('assigned', 'sample_due', 'sample_received', 'attachment_due', 'to_be_verified',):
                can_verify = False
        if not ws_empty:
        # Note: WS adds itself to the skiplist so we have to take it off again
        #       to allow multiple promotions (maybe by more than one self).
            if can_submit and workflow.getInfoFor(ws, 'review_state') == 'open':
                workflow.doActionFor(ws, 'submit')
                skip(ws, 'submit', unskip=True)
            if can_attach and workflow.getInfoFor(ws, 'review_state') == 'attachment_due':
                workflow.doActionFor(ws, 'attach')
                skip(ws, 'attach', unskip=True)
            if can_verify and workflow.getInfoFor(ws, 'review_state') == 'to_be_verified':
                self.REQUEST["workflow_skiplist"].append('verify all analyses')
                workflow.doActionFor(ws, 'verify')
                skip(ws, 'verify', unskip=True)
        else:
            if workflow.getInfoFor(ws, 'review_state') != 'open':
                workflow.doActionFor(ws, 'retract')
                skip(ws, 'retract', unskip=True)

registerType(DuplicateAnalysis, PROJECTNAME)
