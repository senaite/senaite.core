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
