"""ReferenceAnalysis
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget, RecordsField
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.config import STD_TYPES, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims import bikaMessageFactory as _
from zope.interface import implements
from bika.lims import deprecated

#try:
#    from BikaCalendar.config import TOOL_NAME as BIKA_CALENDAR_TOOL # XXX
#except:
#    pass

schema = BikaSchema.copy() + Schema((
    StringField('ReferenceType',
        vocabulary = STD_TYPES,
        widget = SelectionWidget(
            format='select',
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
    DateTimeField('ResultCaptureDate',
        widget = ComputedWidget(
            visible = False,
        ),
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
    ComputedField('SupplierUID',
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
    StringField('ReferenceAnalysesGroupID',
        widget = StringWidget(
            label = _("ReferenceAnalysesGroupID"),
            visible = False,
        ),
    ),
    ComputedField('Keyword',
        expression = "context.getService() and context.getService().getKeyword() or ''",
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
        s = s and s.Title() or ''
        return safe_unicode(s).encode('utf-8')

    def getUncertainty(self, result = None):
        """ Calls self.Service.getUncertainty with either the
            provided result value or self.Result
        """
        return self.getService().getUncertainty(result and result or self.getResult())

    def getSample(self, result = None):
        """ Conform to Analysis
        """
        return self.aq_parent

    def isOutOfRange(self, result=None, specification='lab'):
        """ Check if a result is "out of range".
            if result is None, self.getResult() is called for the result value.
            if specification is None, client specification gets priority from
            lab specification
            Return True, False, spec if out of range
            Return True, True, spec if in shoulder (out, but acceptable)
            Return False, None, None if in range
        """
        result = result is not None and str(result) or self.getResult()

        # if analysis result is not a number, then we assume in range
        try:
            result = float(str(result))
        except ValueError:
            return False, None, None

        service_uid = self.getService().UID()
        spec = self.aq_parent.getResultsRangeDict()
        if service_uid in spec:
            spec_min = None
            spec_max = None
            try:
                spec_min = float(spec[service_uid]['min'])
            except:
                spec_min = None
                pass

            try:
                spec_max = float(spec[service_uid]['max'])
            except:
                spec_max = None
                pass

            if (not spec_min and not spec_max):
                # No min and max values defined
                return False, None, None

            elif spec_min and spec_max \
                and spec_min <= result <= spec_max:
                # min and max values defined
                return False, None, None

            elif spec_min and not spec_max and spec_min <= result:
                # max value not defined
                return False, None, None

            elif not spec_min and spec_max and spec_max >= result:
                # min value not defined
                return False, None, None

            """ check if in 'shoulder' error range - out of range,
                but in acceptable error """
            error = 0
            try:
                error = float(spec[service_uid].get('error', '0'))
            except:
                error = 0
                pass
            error_amount = (result / 100) * error
            error_min = result - error_amount
            error_max = result + error_amount
            if (spec_min and result < spec_min and error_max >= spec_min) or \
               (spec_max and result > spec_max and error_min <= spec_max):
                return True, True, spec[service_uid]
            else:
                return True, False, spec[service_uid]

        else:
            # Analysis without specification values. Assume in range
            return False, None, None

    @deprecated(comment="Note taht isOutOfRange method returns opposite values",
                replacement=isOutOfRange)
    def result_in_range(self, result = None, specification = 'lab'):
        """ Check if the result is in range for the Analysis' service.
            if result is None, self.getResult() is called for the result value.
            specification parameter is ignored.
            Return False,spec if out of range
            Return True,None if in range
            return '1',spec if in shoulder
        """
        outofrange, acceptable, spec = self.isOutOfRange(result, specification)
        return acceptable and '1' or not outofrange, spec

    security.declarePublic('setResult')
    def setResult(self, value, **kw):
        # Always update ResultCapture date when this field is modified
        self.setResultCaptureDate(DateTime())
        self.getField('Result').set(self, value, **kw)

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

registerType(ReferenceAnalysis, PROJECTNAME)
