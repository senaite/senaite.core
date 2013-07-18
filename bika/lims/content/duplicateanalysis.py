"""DuplicateAnalysis
"""
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.config import PROJECTNAME
from bika.lims.content.analysis import schema, Analysis
from bika.lims.interfaces import IDuplicateAnalysis
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
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
        relationship='WorksheetInstrument',
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
        return self.getAnalysis().aq_parent.getSample()

registerType(DuplicateAnalysis, PROJECTNAME)
