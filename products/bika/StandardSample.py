"""StandardSample represents a standard sample used for quality control testing
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
from Products.bika.content.bikaschema import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.bika.config import ManageStandard, ManageBika
from Products.bika.utils import sortable_title
from Products.bika.CustomFields import StandardResultField
from Products.CMFCore.permissions import View

schema = BikaSchema.copy() + Schema((
    StringField('StandardID',
        required = 1,
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'Standard ID',
            label_msgid = 'label_standardid',
            description = 'The ID assigned to the standard sample by the lab',
            description_msgid = 'help_standardid',
            i18n_domain = I18N_DOMAIN,
            visible = {'edit':'hidden'},
        ),
    ),
    StringField('StandardDescription',
        searchable = True,
        widget = StringWidget(
            label = 'Standard description',
            label_msgid = 'label_standarddescription',
            description = 'The standard description',
            description_msgid = 'help_standarddescription',
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
    StandardResultField('Results',
        required = 1,
    ),
    TextField('Notes',
        widget = TextAreaWidget(
            label = 'Notes',
        ),
    ),
    ReferenceField('StandardStock',
        allowed_types = ('StandardStock',),
        relationship = 'StandardSampleStandardStock',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Standard Stock',
            label_msgid = 'label_stock',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('StandardManufacturer',
        allowed_types = ('StandardManufacturer',),
        relationship = 'StandardSampleStandardManufacturer',
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
    ComputedField('StandardSupplierUID',
        index = 'FieldIndex',
        expression = 'context.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('StandardStockUID',
        index = 'FieldIndex',
        expression = 'here.getStandardStock() and here.getStandardStock().UID() or None',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

IdField = schema['id']

class StandardSample(VariableSchemaSupport, BrowserDefaultMixin, BaseFolder):
    security = ClassSecurityInfo()
    archetype_name = 'StandardSample'
    schema = schema
    allowed_content_types = ('StandardAnalysis')
    content_icon = 'standardsample.png'
    immediate_view = 'base_view'
    default_view = 'base_view'
    use_folder_tabs = 0
    global_allow = 0
    filter_content_types = 1
    factory_type_information = {
        'title': 'Standard Sample'
    }
    actions = (
        { 'id': 'view',
          'name': 'View',
          'action': 'string:${object_url}/',
          'permissions': (permissions.View,),
          'visible': True,
        },
        { 'id': 'edit',
          'name': 'Edit',
          'action': 'string:${object_url}/standardsample_edit',
          'permissions': (permissions.ModifyPortalContent,),
          'visible': True,
        },
        { 'id': 'log',
          'name': 'Log',
          'action': 'string:${object_url}/status_log',
          'permissions': (ManageBika,),
        },
        { 'id': 'qc',
          'name': 'QC',
          'action': 'string:${object_url}/report_standardqc_view',
          'permissions': (permissions.View,),
        },
        # document actions
        {'id': 'sticker',
         'name': 'Sticker',
         'action': 'string:${object_url}/standard_sticker',
         'permissions': (View,),
         'category': 'document_actions',
        },

    )

    def Title(self):
        """ Return the Standard ID as title """
        return self.getStandardID()

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

    security.declarePublic('getStandardAnalyses')
    def getStandardAnalyses(self):
        """ return all analyses linked to this standard sample """
        return self.objectValues('StandardAnalysis')

    security.declarePublic('getStandardAnalysesService')
    def getStandardAnalysesService(self, service_uid):
        """ return all analyses linked to this standard sample for a service """
        analyses = []
        for analysis in self.objectValues('StandardAnalysis'):
            if analysis.getServiceUID() == service_uid:
                analyses.append(analysis)
        return analyses

    security.declarePublic('getStandardResult')
    def getStandardResult(self, service_uid):
        """ return the desired result for a specific service """
        for spec in self.getResults():
            if spec['service'] == service_uid:
                result = float(spec['result'])
                min = float(spec['min'])
                max = float(spec['max'])
                return result, min, max
        return None

    security.declarePublic('addStandardAnalysis')
    def addStandardAnalysis(self, service_uid, standard_type):
        """ add an analysis to the sample """
        rc = getToolByName(self, REFERENCE_CATALOG)
        service = rc.lookupObject(service_uid) 

        analysis_id = self.generateUniqueId('StandardAnalysis')
        self.invokeFactory(id = analysis_id, type_name = 'StandardAnalysis')
        analysis = self._getOb(analysis_id)
        calc_type = service.getCalculationType()
        if calc_type:
            calc_code = calc_type.getCalcTypeCode()
        else:
            calc_code = None
        analysis.edit(
            StandardAnalysisID = analysis_id,
            StandardType = standard_type,
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

registerType(StandardSample, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] == 'view':
            a['visible'] = 1
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
