"""ReferenceAnalysis
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget, RecordsField
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.config import STD_TYPES, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims import bikaMessageFactory as _
from zope.interface import implements

#try:
#    from BikaCalendar.config import TOOL_NAME as BIKA_CALENDAR_TOOL # XXX
#except:
#    pass

schema = BikaSchema.copy() + Schema((
    StringField('ReferenceType',
        vocabulary = STD_TYPES,
        widget = SelectionWidget(
            label = _("Reference Type"),
        ),
    ),
    HistoryAwareReferenceField('Service',
        required = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'ReferenceAnalysisAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = _("Analysis Service"),
        )
    ),
    InterimFieldsField('InterimFields',
        widget = BikaRecordsWidget(
            label = _("Calculation Interim Fields"),
        )
    ),
    StringField('Result',
        widget = StringWidget(
            label = _("Result"),
        )
    ),
    StringField('ResultDM',
    ),
    ReferenceField('Attachment',
        multiValued = 1,
        allowed_types = ('Attachment',),
        referenceClass = HoldingReference,
        relationship = 'ReferenceAnalysisAttachment',
    ),
    StringField('Analyst',
    ),
    ReferenceField('Instrument',
        required = 0,
        allowed_types = ('Instrument',),
        relationship = 'WorksheetInstrument',
        referenceClass = HoldingReference,
    ),

    BooleanField('Retested',
        default = False,
        widget = BooleanWidget(
            label = _("Retested"),
        ),
    ),
    ComputedField('ReferenceSampleUID',
        expression = 'context.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ReferenceSupplierUID',
        expression = 'context.aq_parent.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ServiceUID',
        expression = "context.getService() and context.getService().UID() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

class ReferenceAnalysis(BaseContent):
    implements(IReferenceAnalysis)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Service ID as title """
        s = self.getService()
        return s and s.Title() or ''

    def getUncertainty(self, result = None):
        """ Calls self.Service.getUncertainty with either the
            provided result value or self.Result
        """
        return self.getService().getUncertainty(result and result or self.getResult())

    def result_in_range(self, result = None, specification = 'lab'):
        """ Check if the result is in range for the Analysis' service.
            if result is None, self.getResult() is called for the result value.
            specification parameter is ignored.
            Return False,spec if out of range
            Return True,None if in range
            return '1',spec if in shoulder
        """

        result = result and result or self.getResult()

        try:
            result = float(str(result))
        except:
            # if analysis result is not a number, then we assume in range
            return True, None

        service_uid = self.getService().UID()
        specs = self.aq_parent.getResultsRangeDict()
        spec = {'min':-1, 'max':-1, 'error':-1}
        if specs.has_key(service_uid):
            spec = specs[service_uid]
            spec_min = float(spec['min'])
            spec_max = float(spec['max'])

            if spec_min <= result <= spec_max:
                return True, None

            """ check if in 'shoulder' error range - out of range, but in acceptable error """
            error_amount = (result / 100) * float(spec['error'])
            error_min = result - error_amount
            error_max = result + error_amount
            if ((result < spec_min) and (error_max >= spec_min)) or \
               ((result > spec_max) and (error_min <= spec_max)):
                return '1', spec
        else:
            return True, None
        return False, spec

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

registerType(ReferenceAnalysis, PROJECTNAME)
