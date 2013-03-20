"""DuplicateAnalysis
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.config import PROJECTNAME
from bika.lims.content.analysis import schema, Analysis
from bika.lims.interfaces import IDuplicateAnalysis
from zope.interface import implements
from Products.Archetypes.references import HoldingReference
from bika.lims.utils import deprecated

schema = schema.copy() + Schema((
    ReferenceField('Analysis',
        required = 1,
        allowed_types = ('Analysis',),
        referenceClass = HoldingReference,
        relationship = 'DuplicateAnalysisAnalysis',
    ),
    InterimFieldsField('InterimFields',
    ),
    StringField('Result',
    ),
    StringField('ResultDM',
    ),
    BooleanField('Retested',
    ),
    ReferenceField('Attachment',
        multiValued = 1,
        allowed_types = ('Attachment',),
        referenceClass = HoldingReference,
        relationship = 'DuplicateAnalysisAttachment',
    ),

    StringField('Analyst',
    ),
    ReferenceField('Instrument',
        required = 0,
        allowed_types = ('Instrument',),
        relationship = 'WorksheetInstrument',
        referenceClass = HoldingReference,
    ),

    ComputedField('SamplePartition',
        expression = 'context.getAnalysis() and context.getAnalysis().getSamplePartition()',
    ),
    ComputedField('ClientOrderNumber',
        expression = 'context.getAnalysis() and context.getAnalysis().getClientOrderNumber()',
    ),
    ComputedField('Service',
        expression = 'context.getAnalysis() and context.getAnalysis().getService()',
    ),
    ComputedField('ServiceUID',
        expression = 'context.getAnalysis() and context.getAnalysis().getServiceUID()',
    ),
    ComputedField('CategoryUID',
        expression = 'context.getAnalysis() and context.getAnalysis().getCategoryUID()',
    ),
    ComputedField('Calculation',
        expression = 'context.getAnalysis() and context.getAnalysis().getCalculation()',
    ),
    ComputedField('ReportDryMatter',
        expression = 'context.getAnalysis() and context.getAnalysis().getReportDryMatter()',
    ),
    ComputedField('DateReceived',
        expression = 'context.getAnalysis() and context.getAnalysis().getDateReceived()',
    ),
    ComputedField('MaxTimeAllowed',
        expression = 'context.getAnalysis() and context.getAnalysis().getMaxTimeAllowed()',
    ),
    ComputedField('DueDate',
        expression = 'context.getAnalysis() and context.getAnalysis().getDueDate()',
    ),
    ComputedField('Duration',
        expression = 'context.getAnalysis() and context.getAnalysis().getDuration()',
    ),
    ComputedField('Earliness',
        expression = 'context.getAnalysis() and context.getAnalysis().getEarliness()',
    ),
    ComputedField('ClientUID',
        expression = 'context.getAnalysis() and context.getAnalysis().getClientUID()',
    ),
    ComputedField('RequestID',
        expression = 'context.getAnalysis() and context.getAnalysis().getRequestID()',
    ),
    ComputedField('PointOfCapture',
        expression = 'context.getAnalysis() and context.getAnalysis().getPointOfCapture()',
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

    def isOutOfRange(self, result=None, specification=None):
        """ Check if a result is "out of range". (overrides)
            if result is None, self.getResult() is called for the result value.
            specification values allowed='client', 'lab', None
            if specification is None, uses the specifications according this
            priority: QC Duplicate specs > Client specs > Lab specs
            Return True, False, spec if out of range
            Return False, None, None if in range
        """
        if specification == 'client' or specification == 'lab':
            return super(DuplicateAnalysis, self).isOutOfRange(result,
                                                               specification)
        else:
            result = result and result or self.getResult()
            orig_result = self.getResult()

            # if analysis result is not a number, then we assume in range
            try:
                orig_result = float(str(orig_result))
                result = float(str(result))
            except ValueError:
                return False, None, None

            dup_var = float(self.getService().getDuplicateVariation()) or 0
            range_min = result - (orig_result * dup_var / 100)
            range_max = result + (orig_result * dup_var / 100)
            if range_min <= orig_result <= range_max:
                return False, None, None
            else:
                return True, False, {'min': range_min,
                                     'max': range_max,
                                     'error': dup_var}

registerType(DuplicateAnalysis, PROJECTNAME)
