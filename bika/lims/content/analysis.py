# -*- coding: utf-8 -*-

"DuplicateAnalysis uses this as it's base.  This accounts for much confusion."

from AccessControl import getSecurityManager
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from bika.lims import logger
from bika.lims.utils.analysis import format_numeric_result
from plone.indexer import indexer
from Products.ATContentTypes.content import schemata
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget, RecordsField
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, _createObjectByType
from Products.CMFEditions.ArchivistTool import ArchivistRetrieveError
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims import logger
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.permissions import *
from bika.lims.browser.widgets import DurationWidget
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysis, IDuplicateAnalysis, IReferenceAnalysis, \
    IRoutineAnalysis
from bika.lims.interfaces import IReferenceSample
from bika.lims.utils import changeWorkflowState, formatDecimalMark
from bika.lims.utils import drop_trailing_zeros_decimal
from bika.lims.utils.analysis import get_significant_digits
from bika.lims.workflow import skip
from bika.lims.workflow import doActionFor
from decimal import Decimal
from zope.interface import implements
import datetime
import math

@indexer(IAnalysis)
def Priority(instance):
    priority = instance.getPriority()
    if priority:
        return priority.getSortKey()

schema = BikaSchema.copy() + Schema((
    HistoryAwareReferenceField('Service',
        required=1,
        allowed_types=('AnalysisService',),
        relationship='AnalysisAnalysisService',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            label = _("Analysis Service"),
        )
    ),
    HistoryAwareReferenceField('Calculation',
        allowed_types=('Calculation',),
        relationship='AnalysisCalculation',
        referenceClass=HoldingReference,
    ),
    ReferenceField('Attachment',
        multiValued=1,
        allowed_types=('Attachment',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisAttachment',
    ),
    InterimFieldsField('InterimFields',
        widget = BikaRecordsWidget(
            label = _("Calculation Interim Fields"),
        )
    ),
    StringField('Result',
    ),
    DateTimeField('ResultCaptureDate',
        widget = ComputedWidget(
            visible=False,
        ),
    ),
    StringField('ResultDM',
    ),
    BooleanField('Retested',
        default = False,
    ),
    DurationField('MaxTimeAllowed',
        widget = DurationWidget(
            label = _("Maximum turn-around time"),
            description=_("Maximum time allowed for completion of the analysis. "
                            "A late analysis alert is raised when this period elapses"),
        ),
    ),
    DateTimeField('DateAnalysisPublished',
        widget = DateTimeWidget(
            label = _("Date Published"),
        ),
    ),
    DateTimeField('DueDate',
        widget = DateTimeWidget(
            label = _("Due Date"),
        ),
    ),
    IntegerField('Duration',
        widget = IntegerWidget(
            label = _("Duration"),
        )
    ),
    IntegerField('Earliness',
        widget = IntegerWidget(
            label = _("Earliness"),
        )
    ),
    BooleanField('ReportDryMatter',
        default = False,
    ),
    StringField('Analyst',
    ),
    TextField('Remarks',
    ),
    ReferenceField('Instrument',
        required = 0,
        allowed_types = ('Instrument',),
        relationship = 'AnalysisInstrument',
        referenceClass = HoldingReference,
    ),
    ReferenceField('Method',
        required = 0,
        allowed_types = ('Method',),
        relationship = 'AnalysisMethod',
        referenceClass = HoldingReference,
    ),
    ReferenceField('SamplePartition',
        required = 0,
        allowed_types = ('SamplePartition',),
        relationship = 'AnalysisSamplePartition',
        referenceClass = HoldingReference,
    ),
    ComputedField('ClientUID',
        expression = 'context.aq_parent.aq_parent.UID()',
    ),
    ComputedField('ClientTitle',
        expression = 'context.aq_parent.aq_parent.Title()',
    ),
    ComputedField('RequestID',
        expression = 'context.aq_parent.getRequestID()',
    ),
    ComputedField('ClientOrderNumber',
        expression = 'context.aq_parent.getClientOrderNumber()',
    ),
    ComputedField('Keyword',
        expression = 'context.getService().getKeyword()',
    ),
    ComputedField('ServiceTitle',
        expression = 'context.getService().Title()',
    ),
    ComputedField('ServiceUID',
        expression = 'context.getService().UID()',
    ),
    ComputedField('SampleTypeUID',
        expression = 'context.aq_parent.getSample().getSampleType().UID()',
    ),
    ComputedField('SamplePointUID',
        expression = 'context.aq_parent.getSample().getSamplePoint().UID() if context.aq_parent.getSample().getSamplePoint() else None',
    ),
    ComputedField('CategoryUID',
        expression = 'context.getService().getCategoryUID()',
    ),
    ComputedField('CategoryTitle',
        expression = 'context.getService().getCategoryTitle()',
    ),
    ComputedField('PointOfCapture',
        expression = 'context.getService().getPointOfCapture()',
    ),
    ComputedField('DateReceived',
        expression = 'context.aq_parent.getDateReceived()',
    ),
    ComputedField('DateSampled',
        expression = 'context.aq_parent.getSample().getDateSampled()',
    ),
    ComputedField('InstrumentValid',
        expression = 'context.isInstrumentValid()'
    ),
    FixedPointField('Uncertainty',
        widget=DecimalWidget(
            label = _("Uncertainty"),
        ),
    ),
    StringField('DetectionLimitOperand',
    ),

),
)


class Analysis(BaseContent):
    implements(IAnalysis)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def Title(self):
        """ Return the service title as title.
        Some silliness here, for premature indexing, when the service
        is not yet configured.
        """
        try:
            s = self.getService()
            if s:
                s = s.Title()
            if not s:
                s = ''
        except ArchivistRetrieveError:
            s = ''
        return safe_unicode(s).encode('utf-8')

    def updateDueDate(self):
        # set the max hours allowed

        service = self.getService()
        maxtime = service.getMaxTimeAllowed()
        if not maxtime:
            maxtime = {'days': 0, 'hours': 0, 'minutes': 0}
        self.setMaxTimeAllowed(maxtime)
        # set the due date
        # default to old calc in case no calendars
        max_days = float(maxtime.get('days', 0)) + \
                 (
                     (float(maxtime.get('hours', 0)) * 3600 +
                      float(maxtime.get('minutes', 0)) * 60)
                     / 86400
                 )
        part = self.getSamplePartition()
        if part:
            starttime = part.getDateReceived()
            if starttime:
                duetime = starttime + max_days
            else:
                duetime = ''
            self.setDueDate(duetime)

    def getReviewState(self):
        """ Return the current analysis' state"""
        workflow = getToolByName(self, "portal_workflow")
        return workflow.getInfoFor(self, "review_state")

    def getDefaultUncertainty(self, result=None):
        """ Calls self.Service.getUncertainty with either the provided
            result value or self.Result
        """
        return self.getService().getUncertainty(result and result or self.getResult())

    def getUncertainty(self, result=None):
        """ Returns the uncertainty for this analysis and result.
            Returns the value from Schema's Uncertainty field if the
            Service has the option 'Allow manual uncertainty'. Otherwise,
            do a callback to getDefaultUncertainty().
            Returns None if no result specified and the current result
            for this analysis is below or above detections limits.
        """
        serv = self.getService()
        schu = self.Schema().getField('Uncertainty').get(self)
        if result is None and (self.isAboveUpperDetectionLimit() or \
                               self.isBelowLowerDetectionLimit()):
            return None

        if schu and serv.getAllowManualUncertainty() == True:
            try:
                schu = float(schu)
                return schu
            except ValueError:
                # if uncertainty is not a number, return default value
                return self.getDefaultUncertainty(result)
        return self.getDefaultUncertainty(result)

    def setDetectionLimitOperand(self, value):
        """ Sets the detection limit operand for this analysis, so
            the result will be interpreted as a detection limit.
            The value will only be set if the Service has
            'DetectionLimitSelector' field set to True, otherwise,
            the detection limit operand will be set to None.
            See LIMS-1775 for further information about the relation
            amongst 'DetectionLimitSelector' and
            'AllowManualDetectionLimit'.
            https://jira.bikalabs.com/browse/LIMS-1775
        """
        srv = self.getService()
        md = srv.getDetectionLimitSelector() if srv else False
        val = value if (md and value in ('>', '<')) else None
        self.Schema().getField('DetectionLimitOperand').set(self, val)

    def getLowerDetectionLimit(self):
        """ Returns the Lower Detection Limit (LDL) that applies to
            this analysis in particular. If no value set or the
            analysis service doesn't allow manual input of detection
            limits, returns the value set by default in the Analysis
            Service
        """
        operand = self.getDetectionLimitOperand()
        if operand and operand == '<':
            result = self.getResult()
            try:
                return float(result)
            except:
                logger.warn("The result for the analysis %s is a lower "
                            "detection limit, but not floatable: '%s'. "
                            "Returnig AS's default LDL." %
                            (self.id, result))
        return self.getService().getLowerDetectionLimit()

    def getUpperDetectionLimit(self):
        """ Returns the Upper Detection Limit (UDL) that applies to
            this analysis in particular. If no value set or the
            analysis service doesn't allow manual input of detection
            limits, returns the value set by default in the Analysis
            Service
        """
        operand = self.getDetectionLimitOperand()
        if operand and operand == '>':
            result = self.getResult()
            try:
                return float(result)
            except:
                logger.warn("The result for the analysis %s is a lower "
                            "detection limit, but not floatable: '%s'. "
                            "Returnig AS's default LDL." %
                            (self.id, result))
        return self.getService().getUpperDetectionLimit()

    def isBelowLowerDetectionLimit(self):
        """ Returns True if the result is below the Lower Detection
            Limit or if Lower Detection Limit has been manually set
        """
        dl = self.getDetectionLimitOperand()
        if dl and dl == '<':
            return True
        result = self.getResult()
        if result and str(result).strip().startswith('<'):
            return True
        elif result:
            ldl = self.getLowerDetectionLimit()
            try:
                result = float(result)
                return result < ldl
            except:
                pass
        return False

    def isAboveUpperDetectionLimit(self):
        """ Returns True if the result is above the Upper Detection
            Limit or if Upper Detection Limit has been manually set
        """
        dl = self.getDetectionLimitOperand()
        if dl and dl == '>':
            return True
        result = self.getResult()
        if result and str(result).strip().startswith('>'):
            return True
        elif result:
            udl = self.getUpperDetectionLimit()
            try:
                result = float(result)
                return result > udl
            except:
                pass
        return False

    def getDetectionLimits(self):
        """ Returns a two-value array with the limits of detection
            (LDL and UDL) that applies to this analysis in particular.
            If no value set or the analysis service doesn't allow
            manual input of detection limits, returns the value set by
            default in the Analysis Service
        """
        return [self.getLowerDetectionLimit(), self.getUpperDetectionLimit()]

    def isLowerDetectionLimit(self):
        """ Returns True if the result for this analysis represents
            a Lower Detection Limit. Otherwise, returns False
        """
        return self.isBelowLowerDetectionLimit() and \
                self.getDetectionLimitOperand() == '<'

    def isUpperDetectionLimit(self):
        """ Returns True if the result for this analysis represents
            an Upper Detection Limit. Otherwise, returns False
        """
        return self.isAboveUpperDetectionLimit() and \
                self.getDetectionLimitOperand() == '>'

    def getDependents(self):
        """ Return a list of analyses who depend on us
            to calculate their result
        """
        rc = getToolByName(self, REFERENCE_CATALOG)
        dependents = []
        service = self.getService()
        ar = self.aq_parent
        for sibling in ar.getAnalyses(full_objects=True):
            if sibling == self:
                continue
            service = rc.lookupObject(sibling.getServiceUID())
            calculation = service.getCalculation()
            if not calculation:
                continue
            depservices = calculation.getDependentServices()
            dep_keywords = [x.getKeyword() for x in depservices]
            if self.getService().getKeyword() in dep_keywords:
                dependents.append(sibling)
        return dependents

    def getDependencies(self):
        """ Return a list of analyses who we depend on
            to calculate our result.
        """
        siblings = self.aq_parent.getAnalyses(full_objects=True)
        calculation = self.getService().getCalculation()
        if not calculation:
            return []
        dep_services = [d.UID() for d in calculation.getDependentServices()]
        dep_analyses = [a for a in siblings if a.getServiceUID() in dep_services]
        return dep_analyses

    def setResult(self, value, **kw):
        # Always update ResultCapture date when this field is modified
        self.setResultCaptureDate(DateTime())
        # Only allow DL if manually enabled in AS
        val = value
        if val and (val.strip().startswith('>') or val.strip().startswith('<')):
            self.Schema().getField('DetectionLimitOperand').set(self, None)
            oper = '<' if val.strip().startswith('<') else '>'
            srv = self.getService()
            if srv and srv.getDetectionLimitSelector():
                if srv.getAllowManualDetectionLimit():
                    # DL allowed, try to remove the operator and set the
                    # result as a detection limit
                    try:
                        val = val.replace(oper, '', 1)
                        val = str(float(val))
                        self.Schema().getField('DetectionLimitOperand').set(self, oper)
                    except:
                        val = value
                else:
                    # Trying to set a result with an '<,>' operator,
                    # but manual DL not allowed, so override the
                    # value with the service's default LDL or UDL
                    # according to the operator, but only if the value
                    # is not an indeterminate.
                    try:
                        val = val.replace(oper, '', 1)
                        val = str(float(val)) # An indeterminate?
                        if oper == '<':
                            val = srv.getLowerDetectionLimit()
                        else:
                            val = srv.getUpperDetectionLimit()
                        self.Schema().getField('DetectionLimitOperand').set(self, oper)
                    except:
                        # Oops, an indeterminate. Do nothing.
                        val = value
            elif srv:
                # Ooopps. Trying to set a result with an '<,>' operator,
                # but the service doesn't allow this in any case!
                # No need to check for AllowManualDetectionLimit, cause
                # we assume that this will always be False unless
                # DetectionLimitSelector is True. See LIMS-1775 for
                # further information about the relation amongst
                # 'DetectionLimitSelector' and 'AllowManualDetectionLimit'.
                # https://jira.bikalabs.com/browse/LIMS-1775
                # Let's try to remove the operator and set the value as
                # a regular result, but only if not an indeterminate
                try:
                    val = val.replace(oper, '', 1)
                    val = str(float(val))
                except:
                    val = value
        elif not val:
            # Reset DL
            self.Schema().getField('DetectionLimitOperand').set(self, None)
        self.getField('Result').set(self, val, **kw)

        # Uncertainty calculation on DL
        # https://jira.bikalabs.com/browse/LIMS-1808
        if self.isAboveUpperDetectionLimit() or \
           self.isBelowLowerDetectionLimit():
            self.Schema().getField('Uncertainty').set(self, None)

    def setUncertainty(self, unc):
        """ Sets the uncertainty for this analysis. If the result is
            a Detection Limit or the value is below LDL or upper UDL,
            sets the uncertainty value to 0
        """
        # Uncertainty calculation on DL
        # https://jira.bikalabs.com/browse/LIMS-1808
        if self.isAboveUpperDetectionLimit() or \
           self.isBelowLowerDetectionLimit():
            self.Schema().getField('Uncertainty').set(self, None)
        else:
            self.Schema().getField('Uncertainty').set(self, unc)

    def getSample(self):
        # ReferenceSample cannot provide a 'getSample'
        if IReferenceAnalysis.providedBy(self):
            return None
        if IDuplicateAnalysis.providedBy(self) \
                or self.portal_type == 'RejectAnalysis':
            return self.getAnalysis().aq_parent.getSample()
        return self.aq_parent.getSample()

    def getResultsRange(self, specification=None):
        """ Returns the valid results range for this analysis, a
            dictionary with the following keys: 'keyword', 'uid', 'min',
            'max', 'error', 'hidemin', 'hidemax', 'rangecomment'
            Allowed values for specification='ar', 'client', 'lab', None
            If specification is None, the following is the priority to
            get the results range: AR > Client > Lab
            If no specification available for this analysis, returns {}
        """
        rr = {}
        an = self
        while an and an.portal_type in ('DuplicateAnalysis', 'RejectAnalysis'):
            an = an.getAnalysis()

        if specification == 'ar' or specification is None:
            if an.aq_parent and an.aq_parent.portal_type == 'AnalysisRequest':
                key = an.getKeyword()
                rr = an.aq_parent.getResultsRange()
                rr = [r for r in rr if r.get('keyword', '') == an.getKeyword()]
                rr = rr[0] if rr and len(rr) > 0 else {}
            if specification == 'ar' or rr:
                rr['uid'] = self.UID()
                return rr

        specs = an.getAnalysisSpecs(specification)
        rr = specs.getResultsRangeDict() if specs else {}
        rr = rr.get(an.getKeyword(), {}) if rr else {}
        if rr:
            rr['uid'] = self.UID()
        return rr

    def getAnalysisSpecs(self, specification=None):
        """ Retrieves the analysis specs to be applied to this analysis.
            Allowed values for specification= 'client', 'lab', None
            If specification is None, client specification gets priority from
            lab specification.
            If no specification available for this analysis, returns None
        """

        sample = self.getSample()

        # No specifications available for ReferenceSamples
        if IReferenceSample.providedBy(sample):
            return None

        sampletype = sample.getSampleType()
        sampletype_uid = sampletype and sampletype.UID() or ''
        bsc = getToolByName(self, 'bika_setup_catalog')

        # retrieves the desired specs if None specs defined
        if not specification:
            proxies = bsc(portal_type='AnalysisSpec',
                          getClientUID=self.getClientUID(),
                          getSampleTypeUID=sampletype_uid)

            if len(proxies) == 0:
                # No client specs available, retrieve lab specs
                labspecsuid = self.bika_setup.bika_analysisspecs.UID()
                proxies = bsc(portal_type = 'AnalysisSpec',
                          getSampleTypeUID = sampletype_uid)
        else:
            specuid = specification == "client" and self.getClientUID() or \
                    self.bika_setup.bika_analysisspecs.UID()
            proxies = bsc(portal_type='AnalysisSpec',
                              getSampleTypeUID=sampletype_uid,
                              getClientUID=specuid)

        outspecs = None
        for spec in (p.getObject() for p in proxies):
            if self.getKeyword() in spec.getResultsRangeDict():
                outspecs = spec
                break

        return outspecs

    def calculateResult(self, override=False, cascade=False):
        """ Calculates the result for the current analysis if it depends of
            other analysis/interim fields. Otherwise, do nothing
        """
        if self.getResult() and override == False:
            return False

        serv = self.getService()
        calc = self.getCalculation() if self.getCalculation() \
                                     else serv.getCalculation()
        if not calc:
            return False

        mapping = {}

        # Interims' priority order (from low to high):
        # Calculation < Analysis Service < Analysis
        interims = calc.getInterimFields() + \
                   serv.getInterimFields() + \
                   self.getInterimFields()

        # Add interims to mapping
        for i in interims:
            if 'keyword' not in i:
                continue;
            try:
                ivalue = float(i['value'])
                mapping[i['keyword']] = ivalue
            except:
                # Interim not float, abort
                return False

        # Add dependencies results to mapping
        dependencies = self.getDependencies()
        for dependency in dependencies:
            result = dependency.getResult()
            if not result:
                # Dependency without results found
                if cascade:
                    # Try to calculate the dependency result
                    dependency.calculateResult(override, cascade)
                    result = dependency.getResult()
                else:
                    return False
            if result:
                try:
                    result = float(str(result))
                    key = dependency.getKeyword()
                    ldl = dependency.getLowerDetectionLimit()
                    udl = dependency.getUpperDetectionLimit()
                    bdl = dependency.isBelowLowerDetectionLimit()
                    adl = dependency.isAboveUpperDetectionLimit()
                    mapping[key]=result
                    mapping['%s.%s' % (key, 'RESULT')]=result
                    mapping['%s.%s' % (key, 'LDL')]=ldl
                    mapping['%s.%s' % (key, 'UDL')]=udl
                    mapping['%s.%s' % (key, 'BELOWLDL')]=int(bdl)
                    mapping['%s.%s' % (key, 'ABOVEUDL')]=int(adl)
                except:
                    return False

        # Calculate
        formula = calc.getMinifiedFormula()
        formula = formula.replace('[', '%(').replace(']', ')f')
        try:
            formula = eval("'%s'%%mapping" % formula,
                               {"__builtins__": None,
                                'math': math,
                                'context': self},
                               {'mapping': mapping})
            result = eval(formula)
        except TypeError:
            self.setResult("NA")
            return True
        except ZeroDivisionError:
            self.setResult('0/0')
            return True
        except KeyError as e:
            self.setResult("NA")
            return True

        self.setResult(str(result))
        return True

    def getPriority(self):
        """ get priority from AR
        """
        # this analysis may be a Duplicate or Reference Analysis - CAREFUL
        # these types still subclass Analysis.
        if self.portal_type != 'Analysis':
            return None
        # this analysis could be in a worksheet or instrument, careful
        return self.aq_parent.getPriority() \
            if hasattr(self.aq_parent, 'getPriority') else None

    def getPrice(self):
        price = self.getService().getPrice()
        priority = self.getPriority()
        if priority and priority.getPricePremium() > 0:
            price = Decimal(price) + (
                      Decimal(price) * Decimal(priority.getPricePremium())
                      / 100)
        return price

    def getVATAmount(self):
        vat = self.getService().getVAT()
        price = self.getPrice()
        return float(price) * float(vat) / 100

    def getTotalPrice(self):
        return float(self.getPrice()) + float(self.getVATAmount())

    def isInstrumentValid(self):
        """ Checks if the instrument selected for this analysis service
            is valid. Returns false if an out-of-date or uncalibrated
            instrument is assigned. Returns true if the Analysis has
            no instrument assigned or is valid.
        """
        return self.getInstrument().isValid() \
                if self.getInstrument() else True

    def getDefaultInstrument(self):
        """ Returns the default instrument for this analysis according
            to its parent analysis service
        """
        return self.getService().getInstrument() \
            if self.getService().getInstrumentEntryOfResults() \
            else None

    def isInstrumentAllowed(self, instrument):
        """ Checks if the specified instrument can be set for this
            analysis, according to the Method and Analysis Service.
            If the Analysis Service hasn't set 'Allows instrument entry'
            of results, returns always False. Otherwise, checks if the
            method assigned is supported by the instrument specified.
            Returns false, If the analysis hasn't any method assigned.
            NP: The methods allowed for selection are defined at
            Analysis Service level.
            instrument param can be either an uid or an object
        """
        if isinstance(instrument, str):
            uid = instrument
        else:
            uid = instrument.UID()

        return uid in self.getAllowedInstruments()

    def isMethodAllowed(self, method):
        """ Checks if the analysis can follow the method specified.
            Looks for manually selected methods when AllowManualEntry
            is set and instruments methods when AllowInstrumentResultsEntry
            is set.
            method param can be either an uid or an object
        """
        if isinstance(method, str):
            uid = method
        else:
            uid = method.UID()

        return uid in self.getAllowedMethods()

    def getAllowedMethods(self, onlyuids=True):
        """ Returns the allowed methods for this analysis. If manual
            entry of results is set, only returns the methods set
            manually. Otherwise (if Instrument Entry Of Results is set)
            returns the methods assigned to the instruments allowed for
            this Analysis
        """
        service = self.getService()
        uids = []

        if service.getInstrumentEntryOfResults() == True:
            uids = [ins.getRawMethod() for ins in service.getInstruments()]

        else:
            # Get only the methods set manually
            uids = service.getRawMethods()

        if onlyuids == False:
            uc = getToolByName(self, 'uid_catalog')
            meths = [item.getObject() for item in uc(UID=uids)]
            return meths

        return uids

    def getAllowedInstruments(self, onlyuids=True):
        """ Returns the allowed instruments for this analysis. Gets the
            instruments assigned to the allowed methods
        """
        uids = []
        service = self.getService()

        if service.getInstrumentEntryOfResults() == True:
            uids = service.getRawInstruments()

        elif service.getManualEntryOfResults == True:
            meths = self.getAllowedMethods(False)
            for meth in meths:
                uids += meth.getInstrumentUIDs()
            set(uids)

        if onlyuids == False:
            uc = getToolByName(self, 'uid_catalog')
            instrs = [item.getObject() for item in uc(UID=uids)]
            return instrs

        return uids

    def getDefaultMethod(self):
        """ Returns the default method for this Analysis
            according to its current instrument. If the Analysis hasn't
            set yet an Instrument, looks to the Service
        """
        instr = self.getInstrument() \
            if self.getInstrument else self.getDefaultInstrument()
        return instr.getMethod() if instr else None

    def getFormattedResult(self, specs=None, decimalmark='.', sciformat=1):
        """Formatted result:
        1. If the result is a detection limit, returns '< LDL' or '> UDL'
        2. Print ResultText of matching ResultOptions
        3. If the result is not floatable, return it without being formatted
        4. If the analysis specs has hidemin or hidemax enabled and the
           result is out of range, render result as '<min' or '>max'
        5. If the result is below Lower Detection Limit, show '<LDL'
        6. If the result is above Upper Detecion Limit, show '>UDL'
        7. Otherwise, render numerical value
        specs param is optional. A dictionary as follows:
            {'min': <min_val>,
             'max': <max_val>,
             'error': <error>,
             'hidemin': <hidemin_val>,
             'hidemax': <hidemax_val>}
        :param sciformat: 1. The sci notation has to be formatted as aE^+b
                          2. The sci notation has to be formatted as a·10^b
                          3. As 2, but with super html entity for exp
                          4. The sci notation has to be formatted as a·10^b
                          5. As 4, but with super html entity for exp
                          By default 1
        """
        result = self.getResult()

        # 1. The result is a detection limit, return '< LDL' or '> UDL'
        dl = self.getDetectionLimitOperand()
        if dl:
            try:
                res = float(result) # required, check if floatable
                res = drop_trailing_zeros_decimal(res)
                return formatDecimalMark('%s %s' % (dl, res), decimalmark)
            except:
                logger.warn("The result for the analysis %s is a "
                            "detection limit, but not floatable: %s" %
                            (self.id, result))
                return formatDecimalMark(result, decimalmark=decimalmark)

        service = self.getService()
        choices = service.getResultOptions()

        # 2. Print ResultText of matching ResulOptions
        match = [x['ResultText'] for x in choices
                 if str(x['ResultValue']) == str(result)]
        if match:
            return match[0]

        # 3. If the result is not floatable, return it without being formatted
        try:
            result = float(result)
        except:
            return formatDecimalMark(result, decimalmark=decimalmark)

        # 4. If the analysis specs has enabled hidemin or hidemax and the
        #    result is out of range, render result as '<min' or '>max'
        belowmin = False
        abovemax = False
        specs = specs if specs else self.getResultsRange()
        hidemin = specs.get('hidemin', '')
        hidemax = specs.get('hidemax', '')
        try:
            belowmin = hidemin and result < float(hidemin) or False
        except:
            belowmin = False
            pass
        try:
            abovemax = hidemax and result > float(hidemax) or False
        except:
            abovemax = False
            pass

        # 4.1. If result is below min and hidemin enabled, return '<min'
        if belowmin:
            return formatDecimalMark('< %s' % hidemin, decimalmark)

        # 4.2. If result is above max and hidemax enabled, return '>max'
        if abovemax:
            return formatDecimalMark('> %s' % hidemax, decimalmark)

        # Below Lower Detection Limit (LDL)?
        ldl = self.getLowerDetectionLimit()
        if result < ldl:
            # LDL must not be formatted according to precision, etc.
            # Drop trailing zeros from decimal
            ldl = drop_trailing_zeros_decimal(ldl)
            return formatDecimalMark('< %s' % ldl, decimalmark)

        # Above Upper Detection Limit (UDL)?
        udl = self.getUpperDetectionLimit()
        if result > udl:
            # UDL must not be formatted according to precision, etc.
            # Drop trailing zeros from decimal
            udl = drop_trailing_zeros_decimal(udl)
            return formatDecimalMark('> %s' % udl, decimalmark)

        # Render numerical values
        return formatDecimalMark(format_numeric_result(self, result, sciformat=sciformat), decimalmark=decimalmark)

    def getPrecision(self, result=None):
        """
        Returns the precision for the Analysis.
        - ManualUncertainty not set: returns the precision from the
            AnalysisService.
        - ManualUncertainty set and Calculate Precision from Uncertainty
          is also set in Analysis Service: calculates the precision of the
          result according to the manual uncertainty set.
        - ManualUncertainty set and Calculatet Precision from Uncertainty
          not set in Analysis Service: returns the result as-is.
        Further information at AnalysisService.getPrecision()
        """
        serv = self.getService()
        schu = self.Schema().getField('Uncertainty').get(self)
        if schu and serv.getAllowManualUncertainty() == True \
            and serv.getPrecisionFromUncertainty() == True:
            uncertainty = self.getUncertainty(result)
            if uncertainty == 0:
                return 1
            return abs(get_significant_digits(uncertainty))
        else:
            return serv.getPrecision(result)

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

    def guard_sample_transition(self):
        workflow = getToolByName(self, "portal_workflow")
        if workflow.getInfoFor(self, "cancellation_state", "active") == "cancelled":
            return False
        return True

    def guard_retract_transition(self):
        workflow = getToolByName(self, "portal_workflow")
        if workflow.getInfoFor(self, "cancellation_state", "active") == "cancelled":
            return False
        return True

    def guard_receive_transition(self):
        workflow = getToolByName(self, "portal_workflow")
        if workflow.getInfoFor(self, "cancellation_state", "active") == "cancelled":
            return False
        return True

    def guard_publish_transition(self):
        workflow = getToolByName(self, "portal_workflow")
        if workflow.getInfoFor(self, "cancellation_state", "active") == "cancelled":
            return False
        return True

    def guard_import_transition(self):
        workflow = getToolByName(self, "portal_workflow")
        if workflow.getInfoFor(self, "cancellation_state", "active") == "cancelled":
            return False
        return True

    def guard_attach_transition(self):
        if self.portal_type in ("Analysis",
                                "ReferenceAnalysis",
                                "DuplicateAnalysis"):
            if not self.getAttachment():
                service = self.getService()
                if service.getAttachmentOption() == "r":
                    return False
        return True

    def guard_verify_transition(self):
        workflow = getToolByName(self, "portal_workflow")
        mtool = getToolByName(self, "portal_membership")
        checkPermission = mtool.checkPermission
        if workflow.getInfoFor(self, 'cancellation_state', 'active') == "cancelled":
            return False
        # Only Analysis needs to have dependencies checked
        if self.portal_type == "Analysis":
            for d in self.getDependencies():
                review_state = workflow.getInfoFor(d, "review_state")
                if review_state in ("to_be_sampled", "to_be_preserved", "sample_due",
                                    "sample_received", "attachment_due", "to_be_verified"):
                    return False
        # submitter and verifier compared
        # May we verify results that we ourself submitted?
        if checkPermission(VerifyOwnResults, self):
            return True
        # Check for self-submitted Analysis.
        user_id = getSecurityManager().getUser().getId()
        self_submitted = False
        try:
            # https://jira.bikalabs.com/browse/LIMS-2037;
            # Sometimes the workflow history is inexplicably missing!
            review_history = workflow.getInfoFor(self, "review_history")
        except WorkflowException:
            return True
        review_history = self.reverseList(review_history)
        for event in review_history:
            if event.get("action") == "submit":
                if event.get("actor") == user_id:
                    self_submitted = True
                break
        if self_submitted:
            return False
        return True

    def guard_assign_transition(self):
        workflow = getToolByName(self, "portal_workflow")
        if workflow.getInfoFor(self, 'cancellation_state', 'active') == "cancelled":
            return False
        return True

    def guard_unassign_transition(self):
        """ Check permission against parent worksheet
        """
        workflow = getToolByName(self, "portal_workflow")
        mtool = getToolByName(self, "portal_membership")
        ws = self.getBackReferences("WorksheetAnalysis")
        if not ws:
            return False
        ws = ws[0]
        if workflow.getInfoFor(ws, "cancellation_state", "") == "cancelled":
            return False
        if mtool.checkPermission(Unassign, ws):
            return True
        return False

    def workflow_script_receive(self):
        workflow = getToolByName(self, "portal_workflow")
        if workflow.getInfoFor(self, 'cancellation_state', 'active') == "cancelled":
            return False
        # DuplicateAnalysis doesn't have analysis_workflow.
        if self.portal_type == "DuplicateAnalysis":
            return
        if skip(self, "receive"):
            return
        self.updateDueDate()
        self.reindexObject()

    def workflow_script_submit(self):
        # DuplicateAnalysis doesn't have analysis_workflow.
        if self.portal_type == "DuplicateAnalysis":
            return
        if skip(self, "submit"):
            return
        workflow = getToolByName(self, "portal_workflow")
        if workflow.getInfoFor(self, 'cancellation_state', 'active') == "cancelled":
            return False
        ar = self.aq_parent
        self.reindexObject(idxs=["review_state", ])
        # Dependencies are submitted already, ignore them.
        #-------------------------------------------------
        # Submit our dependents
        # Need to check for result and status of dependencies first
        dependents = self.getDependents()
        for dependent in dependents:
            if not skip(dependent, "submit", peek=True):
                can_submit = True
                if not dependent.getResult():
                    can_submit = False
                else:
                    interim_fields = False
                    service = dependent.getService()
                    calculation = service.getCalculation()
                    if calculation:
                        interim_fields = calculation.getInterimFields()
                    if interim_fields:
                        can_submit = False
                if can_submit:
                    dependencies = dependent.getDependencies()
                    for dependency in dependencies:
                        if workflow.getInfoFor(dependency, "review_state") in \
                           ("to_be_sampled", "to_be_preserved",
                            "sample_due", "sample_received",):
                            can_submit = False
                if can_submit:
                    workflow.doActionFor(dependent, "submit")

        # If all analyses in this AR have been submitted
        # escalate the action to the parent AR
        if not skip(ar, "submit", peek=True):
            all_submitted = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ("to_be_sampled", "to_be_preserved",
                    "sample_due", "sample_received",):
                    all_submitted = False
                    break
            if all_submitted:
                workflow.doActionFor(ar, "submit")

        # If assigned to a worksheet and all analyses on the worksheet have been submitted,
        # then submit the worksheet.
        ws = self.getBackReferences("WorksheetAnalysis")
        if ws:
            ws = ws[0]
            # if the worksheet analyst is not assigned, the worksheet can't  be transitioned.
            if ws.getAnalyst() and not skip(ws, "submit", peek=True):
                all_submitted = True
                for a in ws.getAnalyses():
                    if workflow.getInfoFor(a, "review_state") in \
                       ("to_be_sampled", "to_be_preserved",
                        "sample_due", "sample_received", "assigned",):
                        # Note: referenceanalyses and duplicateanalyses can still have review_state = "assigned".
                        all_submitted = False
                        break
                if all_submitted:
                    workflow.doActionFor(ws, "submit")

        # If no problem with attachments, do 'attach' action for this instance.
        can_attach = True
        if not self.getAttachment():
            service = self.getService()
            if service.getAttachmentOption() == "r":
                can_attach = False
        if can_attach:
            dependencies = self.getDependencies()
            for dependency in dependencies:
                if workflow.getInfoFor(dependency, "review_state") in \
                   ("to_be_sampled", "to_be_preserved", "sample_due",
                    "sample_received", "attachment_due",):
                    can_attach = False
        if can_attach:
            try:
                workflow.doActionFor(self, "attach")
            except WorkflowException:
                pass

    def workflow_script_retract(self):
        # DuplicateAnalysis doesn't have analysis_workflow.
        if self.portal_type == "DuplicateAnalysis":
            return
        if skip(self, "retract"):
            return
        ar = self.aq_parent
        workflow = getToolByName(self, "portal_workflow")
        if workflow.getInfoFor(self, 'cancellation_state', 'active') == "cancelled":
            return False
        # We'll assign the new analysis to this same worksheet, if any.
        ws = self.getBackReferences("WorksheetAnalysis")
        if ws:
            ws = ws[0]
        # Rename the analysis to make way for it's successor.
        # Support multiple retractions by renaming to *-0, *-1, etc
        parent = self.aq_parent
        analyses = [x for x in parent.objectValues("Analysis")
                    if x.getId().startswith(self.id)]
        kw = self.getKeyword()
        # LIMS-1290 - Analyst must be able to retract, which creates a new Analysis.
        parent._verifyObjectPaste = str   # I cancel the permission check with this.
        parent.manage_renameObject(kw, "{0}-{1}".format(kw, len(analyses)))
        delattr(parent, '_verifyObjectPaste')
        # Create new analysis and copy values from retracted
        analysis = _createObjectByType("Analysis", parent, kw)
        analysis.edit(
            Service=self.getService(),
            Calculation=self.getCalculation(),
            InterimFields=self.getInterimFields(),
            ResultDM=self.getResultDM(),
            Retested=True,  # True
            MaxTimeAllowed=self.getMaxTimeAllowed(),
            DueDate=self.getDueDate(),
            Duration=self.getDuration(),
            ReportDryMatter=self.getReportDryMatter(),
            Analyst=self.getAnalyst(),
            Instrument=self.getInstrument(),
            SamplePartition=self.getSamplePartition())
        analysis.setDetectionLimitOperand(self.getDetectionLimitOperand())
        analysis.setResult(self.getResult())
        analysis.unmarkCreationFlag()

        # zope.event.notify(ObjectInitializedEvent(analysis))
        changeWorkflowState(analysis,
                            "bika_analysis_workflow", "sample_received")
        if ws:
            ws.addAnalysis(analysis)
        analysis.reindexObject()
        # retract our dependencies
        if not "retract all dependencies" in self.REQUEST["workflow_skiplist"]:
            for dependency in self.getDependencies():
                if not skip(dependency, "retract", peek=True):
                    if workflow.getInfoFor(dependency, "review_state") in ("attachment_due", "to_be_verified",):
                        # (NB: don"t retract if it"s verified)
                        workflow.doActionFor(dependency, "retract")
        # Retract our dependents
        for dep in self.getDependents():
            if not skip(dep, "retract", peek=True):
                if workflow.getInfoFor(dep, "review_state") not in ("sample_received", "retracted"):
                    self.REQUEST["workflow_skiplist"].append("retract all dependencies")
                    # just return to "received" state, no cascade
                    workflow.doActionFor(dep, 'retract')
                    self.REQUEST["workflow_skiplist"].remove("retract all dependencies")
        # Escalate action to the parent AR
        if not skip(ar, "retract", peek=True):
            if workflow.getInfoFor(ar, "review_state") == "sample_received":
                skip(ar, "retract")
            else:
                if not "retract all analyses" in self.REQUEST["workflow_skiplist"]:
                    self.REQUEST["workflow_skiplist"].append("retract all analyses")
                workflow.doActionFor(ar, "retract")
        # Escalate action to the Worksheet (if it's on one).
        ws = self.getBackReferences("WorksheetAnalysis")
        if ws:
            ws = ws[0]
            if not skip(ws, "retract", peek=True):
                if workflow.getInfoFor(ws, "review_state") == "open":
                    skip(ws, "retract")
                else:
                    if not "retract all analyses" in self.REQUEST['workflow_skiplist']:
                        self.REQUEST["workflow_skiplist"].append("retract all analyses")
                    try:
                        workflow.doActionFor(ws, "retract")
                    except WorkflowException:
                        pass
            # Add to worksheet Analyses
            analyses = list(ws.getAnalyses())
            analyses += [analysis, ]
            ws.setAnalyses(analyses)
            # Add to worksheet layout
            layout = ws.getLayout()
            pos = [x["position"] for x in layout
                   if x["analysis_uid"] == self.UID()][0]
            slot = {"position": pos,
                    "analysis_uid": analysis.UID(),
                    "container_uid": analysis.aq_parent.UID(),
                    "type": "a"}
            layout.append(slot)
            ws.setLayout(layout)

    def workflow_script_verify(self):
        # DuplicateAnalysis doesn't have analysis_workflow.
        if self.portal_type == "DuplicateAnalysis":
            return
        if skip(self, "verify"):
            return
        workflow = getToolByName(self, "portal_workflow")
        if workflow.getInfoFor(self, 'cancellation_state', 'active') == "cancelled":
            return False
        self.reindexObject(idxs=["review_state", ])
        # If all analyses in this AR are verified
        # escalate the action to the parent AR
        ar = self.aq_parent
        if not skip(ar, "verify", peek=True):
            all_verified = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ("to_be_sampled", "to_be_preserved", "sample_due",
                    "sample_received", "attachment_due", "to_be_verified"):
                    all_verified = False
                    break
            if all_verified:
                if not "verify all analyses" in self.REQUEST['workflow_skiplist']:
                    self.REQUEST["workflow_skiplist"].append("verify all analyses")
                workflow.doActionFor(ar, "verify")
        # If this is on a worksheet and all it's other analyses are verified,
        # then verify the worksheet.
        ws = self.getBackReferences("WorksheetAnalysis")
        if ws:
            ws = ws[0]
            ws_state = workflow.getInfoFor(ws, "review_state")
            if ws_state == "to_be_verified" and not skip(ws, "verify", peek=True):
                all_verified = True
                for a in ws.getAnalyses():
                    if workflow.getInfoFor(a, "review_state") in \
                       ("to_be_sampled", "to_be_preserved", "sample_due",
                        "sample_received", "attachment_due", "to_be_verified",
                        "assigned"):
                        # Note: referenceanalyses and duplicateanalyses can
                        # still have review_state = "assigned".
                        all_verified = False
                        break
                if all_verified:
                    if not "verify all analyses" in self.REQUEST['workflow_skiplist']:
                        self.REQUEST["workflow_skiplist"].append("verify all analyses")
                    workflow.doActionFor(ws, "verify")

    def workflow_script_publish(self):
        workflow = getToolByName(self, "portal_workflow")
        if workflow.getInfoFor(self, 'cancellation_state', 'active') == "cancelled":
            return False
        # DuplicateAnalysis doesn't have analysis_workflow.
        if self.portal_type == "DuplicateAnalysis":
            return
        if skip(self, "publish"):
            return
        endtime = DateTime()
        self.setDateAnalysisPublished(endtime)
        starttime = self.aq_parent.getDateReceived()
        starttime = starttime or self.created()
        service = self.getService()
        maxtime = service.getMaxTimeAllowed()
        # set the instance duration value to default values
        # in case of no calendars or max hours
        if maxtime:
            duration = (endtime - starttime) * 24 * 60
            maxtime_delta = int(maxtime.get("hours", 0)) * 86400
            maxtime_delta += int(maxtime.get("hours", 0)) * 3600
            maxtime_delta += int(maxtime.get("minutes", 0)) * 60
            earliness = duration - maxtime_delta
        else:
            earliness = 0
            duration = 0
        self.setDuration(duration)
        self.setEarliness(earliness)
        self.reindexObject()

    def workflow_script_cancel(self):
        if skip(self, "cancel"):
            return
        # DuplicateAnalysis doesn't have analysis_workflow.
        if self.portal_type == "DuplicateAnalysis":
            return
        workflow = getToolByName(self, "portal_workflow")
        self.reindexObject(idxs=["worksheetanalysis_review_state", ])
        # If it is assigned to a worksheet, unassign it.
        if workflow.getInfoFor(self, 'worksheetanalysis_review_state') == 'assigned':
            ws = self.getBackReferences("WorksheetAnalysis")[0]
            skip(self, "cancel", unskip=True)
            ws.removeAnalysis(self)

    def workflow_script_attach(self):
        # DuplicateAnalysis doesn't have analysis_workflow.
        if self.portal_type == "DuplicateAnalysis":
            return
        if skip(self, "attach"):
            return
        workflow = getToolByName(self, "portal_workflow")
        self.reindexObject(idxs=["review_state", ])
        # If all analyses in this AR have been attached
        # escalate the action to the parent AR
        ar = self.aq_parent
        ar_state = workflow.getInfoFor(ar, "review_state")
        if ar_state == "attachment_due" and not skip(ar, "attach", peek=True):
            can_attach = True
            for a in ar.getAnalyses():
                if a.review_state in \
                   ("to_be_sampled", "to_be_preserved",
                    "sample_due", "sample_received", "attachment_due",):
                    can_attach = False
                    break
            if can_attach:
                workflow.doActionFor(ar, "attach")
        # If assigned to a worksheet and all analyses on the worksheet have been attached,
        # then attach the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        if ws:
            ws = ws[0]
            ws_state = workflow.getInfoFor(ws, "review_state")
            if ws_state == "attachment_due" and not skip(ws, "attach", peek=True):
                can_attach = True
                for a in ws.getAnalyses():
                    if workflow.getInfoFor(a, "review_state") in \
                       ("to_be_sampled", "to_be_preserved", "sample_due",
                        "sample_received", "attachment_due", "assigned",):
                        # Note: referenceanalyses and duplicateanalyses can still have review_state = "assigned".
                        can_attach = False
                        break
                if can_attach:
                    workflow.doActionFor(ws, "attach")

    def workflow_script_assign(self):
        # DuplicateAnalysis doesn't have analysis_workflow.
        if self.portal_type == "DuplicateAnalysis":
            return
        if skip(self, "assign"):
            return
        workflow = getToolByName(self, "portal_workflow")
        self.reindexObject(idxs=["worksheetanalysis_review_state", ])
        rc = getToolByName(self, REFERENCE_CATALOG)
        wsUID = self.REQUEST["context_uid"]
        ws = rc.lookupObject(wsUID)
        # retract the worksheet to 'open'
        ws_state = workflow.getInfoFor(ws, "review_state")
        if ws_state != "open":
            if "workflow_skiplist" not in self.REQUEST:
                self.REQUEST["workflow_skiplist"] = ["retract all analyses", ]
            else:
                self.REQUEST["workflow_skiplist"].append("retract all analyses")
            allowed_transitions = [t["id"] for t in workflow.getTransitionsFor(ws)]
            if "retract" in allowed_transitions:
                workflow.doActionFor(ws, "retract")
        # If all analyses in this AR have been assigned,
        # escalate the action to the parent AR
        if not skip(self, "assign", peek=True):
            if not self.getAnalyses(worksheetanalysis_review_state="unassigned"):
                try:
                    allowed_transitions = [t["id"] for t in workflow.getTransitionsFor(self)]
                    if "assign" in allowed_transitions:
                        workflow.doActionFor(self, "assign")
                except:
                    pass

    def workflow_script_unassign(self):
        # DuplicateAnalysis doesn't have analysis_workflow.
        if self.portal_type == "DuplicateAnalysis":
            return
        if skip(self, "unassign"):
            return
        workflow = getToolByName(self, "portal_workflow")
        self.reindexObject(idxs=["worksheetanalysis_review_state", ])
        rc = getToolByName(self, REFERENCE_CATALOG)
        wsUID = self.REQUEST["context_uid"]
        ws = rc.lookupObject(wsUID)
        # Escalate the action to the parent AR if it is assigned
        # Note: AR adds itself to the skiplist so we have to take it off again
        #       to allow multiple promotions/demotions (maybe by more than one instance).
        if workflow.getInfoFor(self, "worksheetanalysis_review_state") == "assigned":
            workflow.doActionFor(self, "unassign")
            skip(self, "unassign", unskip=True)
        # If it has been duplicated on the worksheet, delete the duplicates.
        dups = self.getBackReferences("DuplicateAnalysisAnalysis")
        for dup in dups:
            ws.removeAnalysis(dup)
        # May need to promote the Worksheet's review_state
        #  if all other analyses are at a higher state than this one was.
        # (or maybe retract it if there are no analyses left)
        # Note: duplicates, controls and blanks have 'assigned' as a review_state.
        can_submit = True
        can_attach = True
        can_verify = True
        ws_empty = True
        for a in ws.getAnalyses():
            ws_empty = False
            a_state = workflow.getInfoFor(a, "review_state")
            if a_state in \
               ("to_be_sampled", "to_be_preserved", "assigned",
                "sample_due", "sample_received",):
                can_submit = False
            else:
                if not ws.getAnalyst():
                    can_submit = False
            if a_state in \
               ("to_be_sampled", "to_be_preserved", "assigned",
                "sample_due", "sample_received", "attachment_due",):
                can_attach = False
            if a_state in \
               ("to_be_sampled", "to_be_preserved", "assigned", "sample_due",
                "sample_received", "attachment_due", "to_be_verified",):
                can_verify = False
        if not ws_empty:
        # Note: WS adds itself to the skiplist so we have to take it off again
        #       to allow multiple promotions (maybe by more than one instance).
            if can_submit and workflow.getInfoFor(ws, "review_state") == "open":
                workflow.doActionFor(ws, "submit")
                skip(ws, 'unassign', unskip=True)
            if can_attach and workflow.getInfoFor(ws, "review_state") == "attachment_due":
                workflow.doActionFor(ws, "attach")
                skip(ws, 'unassign', unskip=True)
            if can_verify and workflow.getInfoFor(ws, "review_state") == "to_be_verified":
                self.REQUEST['workflow_skiplist'].append("verify all analyses")
                workflow.doActionFor(ws, "verify")
                skip(ws, 'unassign', unskip=True)
        else:
            if workflow.getInfoFor(ws, "review_state") != "open":
                workflow.doActionFor(ws, "retract")
                skip(ws, "retract", unskip=True)


atapi.registerType(Analysis, PROJECTNAME)

