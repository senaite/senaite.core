"""Analysis

$Id: Analysis.py 1902 2009-10-10 12:17:42Z anneline $
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
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.browser.widgets import DurationWidget
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysis
from decimal import Decimal
from zope.interface import implements
import datetime
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')


schema = BikaSchema.copy() + Schema((
    ReferenceField('Service',
        required = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'AnalysisAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = 'Analysis service',
            label_msgid = 'label_analysis',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    ComputedField('ServiceUID',
        index = 'FieldIndex:brains',
        expression = 'context.getService() and context.getService().UID() or ""',
    ),
    ComputedField('Category',
        index = 'FieldIndex:brains',
        expression = 'context.getService() and context.getService().getCategoryName() or ""',
    ),
    ReferenceField('Attachment',
        multiValued = 1,
        allowed_types = ('Attachment',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisAttachment',
    ),
    FixedPointField('Price',
        required = 1,
        widget = DecimalWidget(
            label = 'Price',
            label_msgid = 'label_price',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('Unit',
        widget = StringWidget(
            label_msgid = 'label_unit',
        ),
    ),
    ReferenceField('Calculation',
        allowed_types = ('Calculation',),
        relationship = 'AnalysisCalculation',
        referenceClass = HoldingReference,
    ),
    StringField('Keyword',
    ),
    BooleanField('ReportDryMatter',
        default = False,
    ),
    InterimFieldsField('InterimFields',
        widget = BikaRecordsWidget(
            label = 'Calculation Interim Fields',
            label_msgid = 'label_interim_fields',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('Result',
    ),
    BooleanField('Retested',
        default = False,
    ),
    ComputedField('DateReceived',
        index = 'FieldIndex:brains',
        expression = 'context.aq_parent.getDateReceived()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    DateTimeField('DateAnalysisPublished',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date published',
            label_msgid = 'label_datepublished',
            visible = {'edit':'hidden'},
        ),
    ),
    DurationField('MaxTimeAllowed',
        widget = DurationWidget(
            label = "Maximum time allowed",
            description = 'Maximum time allowed for ' \
                        'publication of results',
            description_msgid = 'help_max_hours_allowed',
        ),
    ),
    DateTimeField('DueDate',
        index = 'DateIndex:brains',
        widget = DateTimeWidget(
            label = 'Due Date'
        ),
    ),
    IntegerField('Duration',
        index = 'FieldIndex',
        widget = IntegerWidget(
            label = 'Duration',
            label_msgid = 'label_duration',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    IntegerField('Earliness',
        index = 'FieldIndex',
        widget = IntegerWidget(
            label = 'Earliness',
            label_msgid = 'label_earliness',
            i18n_domain = I18N_DOMAIN,
        )
    ),

    ###

    ComputedField('ClientUID',
        index = 'FieldIndex',
        expression = 'context.aq_parent.aq_parent.UID()',
    ),
    ComputedField('RequestID',
        index = 'FieldIndex:brains',
        expression = 'context.aq_parent.getRequestID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('PointOfCapture',
        index = 'FieldIndex',
        expression = 'context.getService() and context.getService().getPointOfCapture()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

class Analysis(BaseContent):
    implements(IAnalysis)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _assigned_to_worksheet = False
    _affects_other_analysis = False

    def Title(self):
        """ Return the service title as title """
        # We construct the analyses manually in ar_add_submit,
        # and they are without Service attribute for a moment.
        s = self.getService()
        if s: return s.Title()

    def getUncertainty(self, result=None):
        """ Calls self.Service.getUncertainty with either the provided
            result value or self.Result
        """
        return self.getService().getUncertainty(result and result or self.getResult())

    def getDependents(self):
        """ Return a list of analyses who depend on us
            to calculate their result
            XXX This should recurse
        """
        rc = getToolByName(self, 'reference_catalog')
        dependents = []
        service = self.getService()
        # XXX why does getAnalyses here return a brain without getServiceUID()?
        for sibling in self.aq_parent.getAnalyses(full_objects=True):
            if sibling == self:
                continue
            service = rc.lookupObject(sibling.getServiceUID())
            calculation = service.getCalculation()
            if not calculation:
                continue
            depservices = calculation.getDependentServices()
            if self.getService() in depservices:
                dependents.append(sibling)
            for depservice in depservices:
                keyword = depservice.getKeyword()
                dependents.append(self.aq_parent[keyword])
        return dependents

    def getDependencies(self):
        """ Return a list of analyses who we depend on
            to calculate our result.
        """
        # XXX why does getAnalyses here return a brain without getServiceUID()?
        siblings = self.aq_parent.getAnalyses(full_objects=True)
        calculation = self.getService().getCalculation()
        if not calculation:
            return []
        deps = [d.UID() for d in calculation.getDependentServices()]
        return [a for a in siblings if a.getServiceUID() in deps]


    def result_in_range(self, result=None, specification="lab"):
        """ Check if a result is "in range".
            if result is None, self.getResult() is called for the result value.
            Return False if out of range
            Return True if in range
            return '1' if in shoulder
        """

        if specification == "client":
            client_uid = self.getClientUID()
        else:
            client_uid = None

        result = result and result or self.getResult()

        try:
            result = float(str(result))
        except:
            # if it is not a number we assume it is in range
            return True

        service = self.getService()
        keyword = service.getKeyword()

        proxies = self.portal_catalog(portal_type = 'AnalysisSpec',
                                      getSampleTypeUID = self.aq_parent.getSample().getSampleType().UID())
        a = [p for p in proxies if p.getObject().getClientUID() == client_uid]
        if a:
            spec_obj = a[0].getObject()
            spec = spec_obj.getResultsRangeDict()
        else:
            return True

        if spec.has_key(keyword):
            spec_min = float(spec[keyword]['min'])
            spec_max = float(spec[keyword]['max'])

            if spec_min <= result <= spec_max:
                return True

            """ check if in 'shoulder' error range - out of range, but in acceptable error """
            error_amount =  (result/100)*float(spec[keyword]['error'])
            error_min = result - error_amount
            error_max = result + error_amount
            if ((result < spec_min) and (error_max >= spec_min)) or \
               ((result > spec_max) and (error_min <= spec_max)):
                return '1'
        else:
            return True
        return False

##
##        elif analysis.portal_type == 'DuplicateAnalysis':
##            service = analysis.getService()
##            service_id = service.getId()
##            service_uid = service.UID()
##            wf_tool = self.context.portal_workflow
##            if wf_tool.getInfoFor(analysis, 'review_state', '') == 'rejected':
##                ws_uid = self.context.UID()
##                for orig in self.context.portal_catalog(portal_type = 'RejectAnalysis',
##                                                        getWorksheetUID = ws_uid,
##                                                        getServiceUID = service_uid):
##                    orig_analysis = orig.getObject()
##                    if orig_analysis.getRequest().getRequestID() == analysis.getRequest().getRequestID():
##                        break
##            else:
##                ar = analysis.getRequest()
##                orig_analysis = ar[service_id]
##            orig_result = orig_analysis.getResult()
##            try:
##                orig_result = float(orig_result)
##            except ValueError:
##                return ''
##            dup_variation = service.getDuplicateVariation()
##            dup_variation = dup_variation and dup_variation or 0
##            range_min = result - (result * dup_variation / 100)
##            range_max = result + (result * dup_variation / 100)
##            if range_min <= orig_result <= range_max:
##                result_class = ''
##            else:
##                result_class = 'out_of_range'


    security.declarePublic('getWorksheet')
    def getWorksheet(self):
        tool = getToolByName(self, REFERENCE_CATALOG)
        worksheet = ''
        uids = [uid for uid in
                tool.getBackReferences(self, 'WorksheetAnalysis')]
        if len(uids) == 1:
            reference = uids[0]
            worksheet = tool.lookupObject(reference.sourceUID)

        return worksheet


atapi.registerType(Analysis, PROJECTNAME)
