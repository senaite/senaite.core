"""ReferenceSample represents a reference sample used for quality control testing
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.fields import ReferenceResultsField
from bika.lims.browser.widgets import ReferenceResultsWidget
from bika.lims.browser.widgets import DateTimeWidget as bika_DateTimeWidget
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.config import ManageReference, ManageBika
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IReferenceSample
from bika.lims.utils import sortable_title
from zope.interface import implements
import sys
import time
from bika.lims import bikaMessageFactory as _
from bika.lims.config import I18N_DOMAIN

schema = BikaSchema.copy() + Schema((
    ReferenceField('ReferenceDefinition',
        ## schemata = "",
        allowed_types = ('ReferenceDefinition',),
        relationship = 'ReferenceSampleReferenceDefinition',
        referenceClass = HoldingReference,
##        vocabulary = "GetActiveReferenceDefinitions", # XXX vocabulary, really, for all the references that should only display active?
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Reference Definition',
            description = _(""),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    BooleanField('Blank',
        ## schemata = "",
        default = False,
        widget = BooleanWidget(
            label = _("Blank"),
            description = _("Check this if the reference sample values are zero or 'blank'"),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    BooleanField('Hazardous',
        ## schemata = "",
        default = False,
        widget = BooleanWidget(
            label = _("Hazardous"),
            description = _("Check this box if these reference samples should be treated as hazardous"),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('ReferenceManufacturer',
        ## schemata = "",
        allowed_types = ('ReferenceManufacturer',),
        relationship = 'ReferenceSampleReferenceManufacturer',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Manufacturer',
            description = _(""),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('CatalogueNumber',
        ## schemata = "",
        widget = StringWidget(
            label = 'Catalogue number',
            description = _(""),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('LotNumber',
        ## schemata = "",
        widget = StringWidget(
            label = 'Lot number',
            description = _(""),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    DateTimeField('DateSampled',
        ## schemata = "",
        index = 'DateIndex',
        widget = bika_DateTimeWidget(
            label = 'Date sampled',
            description = _(""),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    DateTimeField('DateReceived',
        ## schemata = "",
        index = 'DateIndex',
        default_method = 'current_date',
        widget = bika_DateTimeWidget(
            label = 'Date received',
            description = _(""),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    DateTimeField('DateOpened',
        ## schemata = "",
        index = 'DateIndex',
        widget = bika_DateTimeWidget(
            label = 'Date opened',
            description = _(""),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    DateTimeField('ExpiryDate',
        ## schemata = "",
        required = 1,
        index = 'DateIndex',
        widget = bika_DateTimeWidget(
            label = 'Expiry date',
            description = _(""),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    DateTimeField('DateExpired',
        ## schemata = "",
        index = 'DateIndex',
        widget = bika_DateTimeWidget(
            label = 'Date expired',
            description = _(""),
            i18n_domain = I18N_DOMAIN,
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DateDisposed',
        ## schemata = "",
        index = 'DateIndex',
        widget = bika_DateTimeWidget(
            label = 'Date disposed',
            description = _(""),
            i18n_domain = I18N_DOMAIN,
            visible = {'edit':'hidden'},
        ),
    ),
    ReferenceResultsField('ReferenceResults',
        ## schemata = "",
        required = 1,
        widget = ReferenceResultsWidget(
            label = "Reference Results",
            description = _(""),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    TextField('Notes',
        ## schemata = "",
        widget = TextAreaWidget(
            label = 'Notes',
            description = _(""),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ComputedField('ReferenceSupplierUID',
        index = 'FieldIndex',
        expression = 'context.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ReferenceDefinitionUID',
        index = 'FieldIndex',
        expression = 'here.getReferenceDefinition() and here.getReferenceDefinition().UID() or None',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
))

##schema['title'].schemata = default

class ReferenceSample(BaseFolder):
    implements(IReferenceSample)
    security = ClassSecurityInfo()
    schema = schema

##    security.declarePublic('getActiveReferenceDefinitions')
##    def getActiveReferenceDefinitions(self):
##        pc = getToolByName(self, 'portal_catalog')
##        defs = pc(portal_type='ReferenceDefinition',
##                  inactive_state='active')
##        return DisplayList(tuple([(d.UID,d.Title) for d in defs]))

    security.declarePublic('current_date')
    def current_date(self):
        return DateTime().strftime("%Y-%m-%d")

    security.declarePublic('getSpecCategories')
    def getSpecCategories(self):
        tool = getToolByName(self, REFERENCE_CATALOG)
        categories = []
        for spec in self.getReferenceResults():
            service = tool.lookupObject(spec['uid'])
            if service.getCategoryUID() not in categories:
                categories.append(service.getCategoryUID())
        return categories

    security.declarePublic('getResultsRangeDict')
    def getResultsRangeDict(self):
        specs = {}
        for spec in self.getReferenceResults():
            uid = spec['uid']
            specs[uid] = {}
            specs[uid]['result'] = spec['result']
            specs[uid]['min'] = spec['min']
            specs[uid]['max'] = spec['max']
            specs[uid]['error'] = spec['error']
        return specs

    security.declarePublic('getResultsRangeSorted')
    def getResultsRangeSorted(self):
        tool = getToolByName(self, REFERENCE_CATALOG)

        cats = {}
        for spec in self.getReferenceResults():
            service = tool.lookupObject(spec['uid'])
            service_title = service.Title()
            category = service.getCategoryName()
            if not cats.has_key(category):
                cats[category] = {}

            cat = cats[category]
            cat[service_title] = {'category': category,
                                  'service': service_title,
                                  'id': service.getId(),
                                  'unit': service.getUnit(),
                                  'result': spec['result'],
                                  'min': spec['min'],
                                  'max': spec['max'],
                                  'error': spec['error']}

        cat_keys = cats.keys()
        cat_keys.sort(lambda x, y:cmp(x.lower(), y.lower()))
        sorted_specs = []
        for cat in cat_keys:
            services = cats[cat]
            service_keys = services.keys()
            service_keys.sort(lambda x, y:cmp(x.lower(), y.lower()))
            for service_key in service_keys:
                sorted_specs.append(services[service_key])

        return sorted_specs

    security.declarePublic('getReferenceAnalyses')
    def getReferenceAnalyses(self):
        """ return all analyses linked to this reference sample """
        return self.objectValues('ReferenceAnalysis')

    security.declarePublic('getReferenceAnalysesService')
    def getReferenceAnalysesService(self, service_uid):
        """ return all analyses linked to this reference sample for a service """
        analyses = []
        for analysis in self.objectValues('ReferenceAnalysis'):
            if analysis.getServiceUID() == service_uid:
                analyses.append(analysis)
        return analyses

    security.declarePublic('getReferenceResult')
    def getReferenceResult(self, service_uid):
        """ return the desired result for a specific service """
        for spec in self.getReferenceResults():
            if spec['uid'] == service_uid:
                result = float(spec['result'])
                min = float(spec['min'])
                max = float(spec['max'])
                error = float(spec['error'])
                return result, min, max, error
        return None

    security.declarePublic('addReferenceAnalysis')
    def addReferenceAnalysis(self, service_uid, reference_type):
        """ add an analysis to the sample """
        rc = getToolByName(self, REFERENCE_CATALOG)
        service = rc.lookupObject(service_uid)

        analysis_id = self.generateUniqueId('ReferenceAnalysis')
        self.invokeFactory(id = analysis_id, type_name = 'ReferenceAnalysis')
        analysis = self._getOb(analysis_id)
        calculation = service.getCalculation()
        interim_fields = calculation and calculation.getInterimFields() or []

        analysis.edit(
            ReferenceAnalysisID = analysis_id,
            ReferenceType = reference_type,
            Service = service_uid,
            Unit = service.getUnit(),
            Calculation = calculation,
            InterimFields = interim_fields,
            ServiceUID = service.UID(),
        )
        analysis.processForm()
        analysis.reindexObject()
        return analysis.UID()

    security.declarePublic('getServices')
    def getServices(self):
        """ get all services for this Sample """
        tool = getToolByName(self, REFERENCE_CATALOG)
        services = []
        for spec in self.getReferenceResults():
            service = tool.lookupObject(spec['uid'])
            services.append(service)
        return services

    # workflow methods
    #

    def workflow_script_expire(self, state_info):
        """ expire sample """
        self.setDateExpired(DateTime())
        self.reindexObject()

    def workflow_script_dispose(self, state_info):
        """ expire sample """
        self.setDateDisposed(DateTime())
        self.reindexObject()

registerType(ReferenceSample, PROJECTNAME)
