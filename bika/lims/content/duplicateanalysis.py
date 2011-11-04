"""DuplicateAnalysis
"""
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.analysis import schema,Analysis
from bika.lims.interfaces import IDuplicateAnalysis
from zope.interface import implements

schema = schema.copy() + Schema((
    ReferenceField('Analysis',
        required = 1,
        allowed_types = ('Analysis',),
        relationship = 'DuplicateAnalysisAnalysis',
    ),
    InterimFieldsField('InterimFields',
    ),
    StringField('Result',
    ),
    BooleanField('Retested',
    ),
    DateTimeField('DateAnalysisPublished',
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
    ComputedField('Attachment',
        expression = 'context.getAnalysis() and context.getAnalysis().getAttachment()',
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
    schema = schema

    def result_in_range(self, result=None, specification="lab"):
        """ Check if a result is "in range".
            if result is None, self.getResult() is called for the result value.
            Return False,spec if out of range
            Return True,None if in range
        """

        orig_result = self.getAnalysis().getResult()
        # if our Analysis' result is not a number, then we assume in range
        try:
            orig_result = float(str(orig_result))
            result = float(str(result))
        except ValueError:
            return True
        dup_variation = float(self.getService().getDuplicateVariation()) or 0
        range_min = result - (orig_result * dup_variation / 100)
        range_max = result + (orig_result * dup_variation / 100)
        if range_min <= orig_result <= range_max:
            return True, None
        else:
            return False, {'min':range_min,
                           'max':range_max,
                           'error':dup_variation}

registerType(DuplicateAnalysis, PROJECTNAME)
