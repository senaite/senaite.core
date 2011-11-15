"""Analysis

$Id: Analysis.py 1902 2009-10-10 12:17:42Z anneline $
test update
"""

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
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.browser.widgets import DurationWidget
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysis
from bika.lims import logger
from decimal import Decimal
from zope.interface import implements
from Products.CMFEditions.ArchivistTool import ArchivistRetrieveError
import datetime

schema = BikaSchema.copy() + Schema((
    HistoryAwareReferenceField('Service',
        required = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'AnalysisAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = _("Analysis service"),
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
    BooleanField('Retested',
        default = False,
    ),
    DurationField('MaxTimeAllowed',
        widget = DurationWidget(
            label = _("Maximum time allowed"),
            description = _("Maximum time allowed for "
                            "publication of results"),
        ),
    ),
    DateTimeField('DateAnalysisPublished',
        widget = DateTimeWidget(
            label = _("Date published"),
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
    ###

    ComputedField('ClientUID',
        expression = 'context.aq_parent.aq_parent.UID()',
    ),
    ComputedField('RequestID',
        expression = 'context.aq_parent.getRequestID()',
    ),
    ComputedField('ServiceUID',
        expression = 'context.getService() and context.getService().UID() or ""',
    ),
    ComputedField('CategoryUID',
        expression = 'context.getService() and context.getService().getCategoryUID() or ""',
    ),
    ComputedField('PointOfCapture',
        expression = 'context.getService() and context.getService().getPointOfCapture()',
    ),
    ComputedField('DateReceived',
        expression = 'context.aq_parent.getDateReceived()',
    ),
),
)

class Analysis(BaseContent):
    implements(IAnalysis)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _affects_other_analysis = False

    def Title(self):
        """ Return the service title as title """
        # We construct the analyses manually in ar_add_submit,
        # and they are without Service attribute for a moment.
        try:
            s = self.getService()
        except ArchivistRetrieveError:
            # XXX premature indexing
            return ""
        if s: return s.Title()

    def getUncertainty(self, result=None):
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
        for sibling in ar.getAnalyses(full_objects=True):
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
        siblings = self.aq_parent.getAnalyses(full_objects=True)
        calculation = self.getService().getCalculation()
        if not calculation:
            return []
        dep_services = [d.UID() for d in calculation.getDependentServices()]
        dep_analyses = [a for a in siblings if a.getServiceUID() in dep_services]
        return dep_analyses

    def result_in_range(self, result=None, specification="lab"):
        """ Check if a result is "in range".
            if result is None, self.getResult() is called for the result value.
            Return False,failed_spec if out of range
            Return True,None if in range
            return '1',None if in shoulder
        """

        client_uid = specification == "client" and self.getClientUID() or None

        result = result and result or self.getResult()

        # if it is not a number we assume it is in range
        try:
            result = float(str(result))
        except ValueError:
            return True, None

        service = self.getService()
        keyword = service.getKeyword()
        sampletype = self.aq_parent.getSample().getSampleType()
        sampletype_uid = sampletype and sampletype.UID() or ''

        proxies = self.portal_catalog(portal_type = 'AnalysisSpec',
                                      getSampleTypeUID = sampletype_uid)
        a = [p for p in proxies if p.getObject().getClientUID() == client_uid]
        if a:
            spec_obj = a[0].getObject()
            spec = spec_obj.getResultsRangeDict()
        else:
            # if no range is specified we assume it is in range
            return True, None

        if spec.has_key(keyword):
            spec_min = float(spec[keyword]['min'])
            spec_max = float(spec[keyword]['max'])

            if spec_min <= result <= spec_max:
                return True, None

            """ check if in 'shoulder' error range - out of range, but in acceptable error """
            error_amount = (result/100)*float(spec[keyword]['error'])
            error_min = result - error_amount
            error_max = result + error_amount
            if ((result < spec_min) and (error_max >= spec_min)) or \
               ((result > spec_max) and (error_min <= spec_max)):
                return '1', spec[keyword]
        else:
            return True, None
        return False, spec[keyword]

atapi.registerType(Analysis, PROJECTNAME)
