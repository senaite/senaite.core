"""ReferenceSample represents a reference sample used for quality control testing
"""
import sys
import time
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.config import ManageReference, ManageBika
from bika.lims.utils import sortable_title
from bika.lims.browser.fields import ReferenceResultField
from Products.CMFCore.permissions import View

schema = BikaSchema.copy() + Schema((
    StringField('ReferenceID',
        required = 1,
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'Reference ID',
            label_msgid = 'label_referenceid',
            description = 'The ID assigned to the reference sample by the lab',
            description_msgid = 'help_referenceid',
            i18n_domain = I18N_DOMAIN,
            visible = {'edit':'hidden'},
        ),
    ),
    StringField('ReferenceDescription',
        searchable = True,
        widget = StringWidget(
            label = 'Reference description',
            label_msgid = 'label_referencedescription',
            description = 'The reference description',
            description_msgid = 'help_referencedescription',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('CatalogueNumber',
        widget = StringWidget(
            label = 'Catalogue number',
            label_msgid = 'label_calaloguenumber',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('LotNumber',
        widget = StringWidget(
            label = 'Lot number',
            label_msgid = 'label_lotnumber',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceResultField('Results',
        required = 1,
    ),
    TextField('Notes',
        widget = TextAreaWidget(
            label = 'Notes',
        ),
    ),
    ReferenceField('ReferenceDefinition',
        allowed_types = ('ReferenceDefinition',),
        relationship = 'ReferenceSampleReferenceDefinition',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Reference Definition',
            label_msgid = 'label_reference_definition',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('ReferenceManufacturer',
        allowed_types = ('ReferenceManufacturer',),
        relationship = 'ReferenceSampleReferenceManufacturer',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Manufacturer',
            label_msgid = 'label_manufacturer',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    DateTimeField('ExpiryDate',
        required = 1,
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Expiry date',
            label_msgid = 'label_expirydate',
        ),
    ),
    DateTimeField('DateSampled',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date sampled',
            label_msgid = 'label_datesampled',
        ),
    ),
    DateTimeField('DateReceived',
        index = 'DateIndex',
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = 'Date received',
            label_msgid = 'label_datereceived',
        ),
    ),
    DateTimeField('DateOpened',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date opened',
            label_msgid = 'label_dateopened',
        ),
    ),
    DateTimeField('DateExpired',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date expired',
            label_msgid = 'label_dateexpired',
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DateDisposed',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date disposed',
            label_msgid = 'label_datedisposed',
            visible = {'edit':'hidden'},
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
),
)

class ReferenceSample(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema

    def Title(self):
        """ Return the Reference ID as title """
        return self.getReferenceID()

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    security.declarePublic('getSpecCategories')
    def getSpecCategories(self):
        tool = getToolByName(self, REFERENCE_CATALOG)
        categories = []
        for spec in self.getResults():
            service = tool.lookupObject(spec['service'])
            if service.getCategoryUID() not in categories:
                categories.append(service.getCategoryUID())
        return categories

    security.declarePublic('getResultsRangeDict')
    def getResultsRangeDict(self):
        specs = {}
        for spec in self.getResults():
            uid = spec['service']
            specs[uid] = {}
            specs[uid]['result'] = spec['result']
            specs[uid]['min'] = spec['min']
            specs[uid]['max'] = spec['max']
        return specs

    security.declarePublic('getResultsRangeSorted')
    def getResultsRangeSorted(self):
        tool = getToolByName(self, REFERENCE_CATALOG)

        cats = {}
        for spec in self.getResults():
            service = tool.lookupObject(spec['service'])
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
                                  'max': spec['max']}

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
        for spec in self.getResults():
            if spec['service'] == service_uid:
                result = float(spec['result'])
                min = float(spec['min'])
                max = float(spec['max'])
                return result, min, max
        return None

    security.declarePublic('addReferenceAnalysis')
    def addReferenceAnalysis(self, service_uid, reference_type):
        """ add an analysis to the sample """
        rc = getToolByName(self, REFERENCE_CATALOG)
        service = rc.lookupObject(service_uid)

        analysis_id = self.generateUniqueId('ReferenceAnalysis')
        self.invokeFactory(id = analysis_id, type_name = 'ReferenceAnalysis')
        analysis = self._getOb(analysis_id)
        calc_type = service.getCalculationType()
        if calc_type:
            calc_code = calc_type.getCalcTypeCode()
        else:
            calc_code = None
        analysis.edit(
            ReferenceAnalysisID = analysis_id,
            ReferenceType = reference_type,
            Service = service_uid,
            Unit = service.getUnit(),
            CalcType = calc_code,
            ServiceUID = service.UID(),
        )
        analysis.reindexObject()
        return analysis.UID()

    security.declarePublic('getServices')
    def getServices(self):
        """ get all services for this Sample """
        tool = getToolByName(self, REFERENCE_CATALOG)
        services = []
        for spec in self.getResults():
            service = tool.lookupObject(spec['service'])
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
