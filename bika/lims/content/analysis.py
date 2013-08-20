from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.content import schemata
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget, RecordsField
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.CMFEditions.ArchivistTool import ArchivistRetrieveError
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.permissions import Unassign
from bika.lims.browser.widgets import DurationWidget
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysis
from decimal import Decimal
from zope.interface import implements
from bika.lims import deprecated
import datetime
import math

schema = BikaSchema.copy() + Schema((
    HistoryAwareReferenceField('Service',
        required = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'AnalysisAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = _("Analysis Service"),
        )
    ),
    HistoryAwareReferenceField('Calculation',
        allowed_types = ('Calculation',),
        relationship = 'AnalysisCalculation',
        referenceClass = HoldingReference,
    ),
    ReferenceField('Attachment',
        multiValued = 1,
        allowed_types = ('Attachment',),
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
            visible = False,
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
            description = _("Maximum time allowed for completion of the analysis. "
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
        relationship = 'WorksheetInstrument',
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
        expression = 'context.aq_parent.getSample().getSamplePoint().UID()',
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
            maxtime = {'days':0, 'hours':0, 'minutes':0}
        self.setMaxTimeAllowed(maxtime)
        # set the due date
        # default to old calc in case no calendars
        max_days = float(maxtime.get('days', 0)) + \
                 (
                     (float(maxtime.get('hours', 0)) * 3600 + \
                      float(maxtime.get('minutes', 0)) * 60)
                     / 86400
                 )
        part = self.getSamplePartition()
        starttime = part.getDateReceived()
        if starttime:
            duetime = starttime + max_days
        else:
            duetime = ''
        self.setDueDate(duetime)

    def getUncertainty(self, result = None):
        """ Calls self.Service.getUncertainty with either the provided
            result value or self.Result
        """
        return self.getService().getUncertainty(result and result or self.getResult())

    def getDependents(self):
        """ Return a list of analyses who depend on us
            to calculate their result
        """
        rc = getToolByName(self, REFERENCE_CATALOG)
        dependents = []
        service = self.getService()
        ar = self.aq_parent
        for sibling in ar.getAnalyses(full_objects = True):
            if sibling == self:
                continue
            service = rc.lookupObject(sibling.getServiceUID())
            calculation = service.getCalculation()
            if not calculation:
                continue
            depservices = calculation.getDependentServices()
            if self.getService() in depservices:
                dependents.append(sibling)
        return dependents

    def getDependencies(self):
        """ Return a list of analyses who we depend on
            to calculate our result.
        """
        siblings = self.aq_parent.getAnalyses(full_objects = True)
        calculation = self.getService().getCalculation()
        if not calculation:
            return []
        dep_services = [d.UID() for d in calculation.getDependentServices()]
        dep_analyses = [a for a in siblings if a.getServiceUID() in dep_services]
        return dep_analyses

    def setResult(self, value, **kw):
        # Always update ResultCapture date when this field is modified
        self.setResultCaptureDate(DateTime())
        self.getField('Result').set(self, value, **kw)

    def getAnalysisSpecs(self, specification=None):
        """ Retrieves the analysis specs to be applied to this analysis.
            Allowed values for specification= 'client', 'lab', None
            If specification is None, client specification gets priority from
            lab specification.
            If no specification available for this analysis, returns None
        """

        sampletype = self.getSample().getSampleType()
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
                proxies = bsc(portal_type='AnalysisSpec',
                              getSampleTypeUID=sampletype_uid,
                              getClientUID=labspecsuid)
        else:
            specuid = specification == "client" and self.getClientUID() or \
                    self.bika_setup.bika_analysisspecs.UID()
            proxies = bsc(portal_type='AnalysisSpec',
                              getSampleTypeUID=sampletype_uid,
                              getClientUID=specuid)

        return (proxies and len(proxies) > 0) and proxies[0].getObject() or None

    def isOutOfRange(self, result=None, specification=None):
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

        specs = self.getAnalysisSpecs(specification)
        if specs == None:
            # No specs available, assume in range
            return False, None, None

        keyword = self.getService().getKeyword()
        spec = specs.getResultsRangeDict()
        if keyword in spec:
            spec_min = None
            spec_max = None
            try:
                spec_min = float(spec[keyword]['min'])
            except:
                spec_min = None
                pass

            try:
                spec_max = float(spec[keyword]['max'])
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
                error = float(spec[keyword].get('error', '0'))
            except:
                error = 0
                pass
            error_amount = (result / 100) * error
            error_min = result - error_amount
            error_max = result + error_amount
            if (spec_min and result < spec_min and error_max >= spec_min) or \
               (spec_max and result > spec_max and error_min <= spec_max):
                return True, True, spec[keyword]
            else:
                return True, False, spec[keyword]

        else:
            # Analysis without specification values. Assume in range
            return False, None, None

    @deprecated(comment="Note taht isOutOfRange method returns opposite values",
                replacement=isOutOfRange)
    def result_in_range(self, result = None, specification = "lab"):
        """ Check if a result is "in range".
            if result is None, self.getResult() is called for the result value.
            Return False,failed_spec if out of range
            Return True,None if in range
            return '1',None if in shoulder
        """
        outofrange, acceptable, spec = self.isOutOfRange(result, specification)
        return acceptable and '1' or not outofrange, spec

    def getSample(self):
        return self.aq_parent.getSample()

    def calculateResult(self, override=False, cascade=False):
        """ Calculates the result for the current analysis if it depends of
            other analysis/interim fields. Otherwise, do nothing
        """

        if self.getResult() and override == False:
            return False

        calculation = self.getService().getCalculation()
        if not calculation:
            return False

        mapping = {}

        # Add interims to mapping
        for interimuid, interimdata in self.getInterimFields():
            for i in interimdata:
                try:
                    ivalue = float(i['value'])
                    mapping[i['keyword']] = ivalue
                except:
                    # Interim not float, abort
                    return False

        # Add calculation's hidden interim fields to mapping
        for field in calculation.getInterimFields():
            if field['keyword'] not in mapping.keys():
                if field.get('hidden', False):
                    try:
                        ivalue = float(field['value'])
                        mapping[field['keyword']] = ivalue
                    except:
                        return False

        # Add Analysis Service interim defaults to mapping
        service = self.getService()
        for field in service.getInterimFields():
            if field['keyword'] not in mapping.keys():
                if field.get('hidden', False):
                    try:
                        ivalue = float(field['value'])
                        mapping[field['keyword']] = ivalue
                    except:
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
                    if result:
                        try:
                            result = float(str(result))
                            mapping[dependency.getKeyword()] = result
                        except:
                            return False
                else:
                    return False
            else:
                # Result must be float
                try:
                    result = float(str(result))
                    mapping[dependency.getKeyword()] = result
                except:
                    return False

        # Calculate
        formula = calculation.getFormula()
        formula = formula.replace('[', '%(').replace(']', ')f')
        try:
            formula = eval("'%s'%%mapping" % formula,
                               {"__builtins__":None,
                                'math':math,
                                'context':self},
                               {'mapping': mapping})
            result = eval(formula)
        except TypeError:
            self.setResult("NA")
            return True
        except ZeroDivisionError:
            self.setResult('0/0')
            return True
        except KeyError, e:
            self.setResult("NA")
            return True

        precision = service.getPrecision()
        result = (precision and result) \
            and str("%%.%sf" % precision) % result \
            or result
        self.setResult(result)
        return True

    def guard_unassign_transition(self):
        """ Check permission against parent worksheet
        """
        wf = getToolByName(self, 'portal_workflow')
        mtool = getToolByName(self, 'portal_membership')
        ws = self.getBackReferences('WorksheetAnalysis')
        if not ws:
            return False
        ws = ws[0]
        if wf.getInfoFor(ws, 'cancellation_state', '') == "cancelled":
            return False
        if mtool.checkPermission(Unassign, ws):
            return True
        return False

    def guard_assign_transition(self):
        """
        """
        return True


atapi.registerType(Analysis, PROJECTNAME)
