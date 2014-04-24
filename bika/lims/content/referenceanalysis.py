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
from plone.app.blob.field import BlobField

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
    TextField('Remarks',
    ),
    ReferenceField(
        'Instrument',
        required=0,
        allowed_types=('Instrument',),
        relationship='AnalysisInstrument',
        referenceClass=HoldingReference,
    ),
    ReferenceField('Method',
        required = 0,
        allowed_types = ('Method',),
        relationship = 'AnalysisMethod',
        referenceClass = HoldingReference,
    ),
    BlobField('RetractedAnalysesPdfReport',
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

    def isInstrumentValid(self):
        """ Checks if the instrument selected for this analysis
            is valid. Returns false if an out-of-date or uncalibrated
            instrument is assigned. Returns true if the Analysis has
            no instrument assigned or is valid.
        """
        # TODO : Remove when analysis - instrument being assigned directly
        if not self.getInstrument():
            instr = self.getService().getInstrument() \
                    if self.getService().getInstrumentEntryOfResults() \
                    else None
            if instr:
                self.setInstrument(instr)
        # ---8<--------

        return self.getInstrument().isValid() \
                if self.getInstrument() else True

    def isInstrumentAllowed(self, instrument):
        """ Checks if the specified instrument can be set for this
            analysis, according to the Method and Analysis Service.
            If the Analysis Service hasn't set 'Allows instrument entry'
            of results, returns always False. Otherwise, checks if the
            method assigned is supported by the instrument specified.
            The behavoir when no method assigned is different from
            Regular analyses: when no method assigned, the available
            methods for the analysis service are checked and returns
            true if at least one of the methods has support for the
            instrument specified.
        """
        service = self.getService()
        if service.getInstrumentEntryOfResults() == False:
            return False

        if isinstance(instrument, str):
            uid = instrument
        else:
            uid = instrument.UID()

        method = self.getMethod()
        instruments = []
        if not method:
            # Look for Analysis Service methods and instrument support
            instruments = service.getRawInstruments()
        else:
            instruments = method.getInstrumentUIDs()

        return uid in instruments

    def isMethodAllowed(self, method):
        """ Checks if the ref analysis can follow the method specified.
            Looks for manually selected methods when AllowManualResultsEntry
            is set and looks for instruments methods when
            AllowInstrumentResultsEntry is set.
            method param can be either an uid or an object
        """
        if isinstance(method, str):
            uid = method
        else:
            uid = method.UID()

        service = self.getService()
        if service.getManualEntryOfResults() == True \
            and uid in service.getRawMethods():
            return True

        if service.getInstrumentEntryOfResults() == True:
            for ins in service.getInstruments():
                if uid == ins.getRawMethod():
                    return True

        return False

    def getAnalyst(self):
        """ Returns the identifier of the assigned analyst. If there is
            no analyst assigned, and this analysis is attached to a
            worksheet, retrieves the analyst assigned to the parent
            worksheet
        """
        field = self.getField('Analyst')
        analyst = field and field.get(self) or ''
        if not analyst:
            # Is assigned to a worksheet?
            wss = self.getBackReferences('WorksheetAnalysis')
            if len(wss) > 0:
                analyst = wss[0].getAnalyst()
                field.set(self, analyst)
        return analyst if analyst else ''

    def getAnalystName(self):
        """ Returns the name of the currently assigned analyst
        """
        mtool = getToolByName(self, 'portal_membership')
        analyst = self.getAnalyst().strip()
        analyst_member = mtool.getMemberById(analyst)
        if analyst_member != None:
            return analyst_member.getProperty('fullname')
        else:
            return ''

registerType(ReferenceAnalysis, PROJECTNAME)
