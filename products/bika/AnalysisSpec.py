"""Analysis result range specifications for a client

$Id: AnalysisSpec.py 443 2006-12-13 23:19:39Z anneline $
"""
import sys
import time
from types import ListType, TupleType
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import delete_objects
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import ListFolderContents, View
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.utils import shasattr
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.bika.BikaContent import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME 
from Products.bika.CustomFields import AnalysisSpecField

schema = BikaSchema.copy() + Schema((
    ReferenceField('SampleType',
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SampleType',),
        relationship = 'AnalysisSpecSampleType',
        referenceClass = HoldingReference,
    ),
    AnalysisSpecField('ResultsRange',
        required = 1,
    ),
    ComputedField('ClientUID',
        index = 'FieldIndex',
        expression = 'here.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SampleTypeUID',
        index = 'FieldIndex',
        expression = 'here.getSampleType().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
))
IdField = schema['id']
TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}

class AnalysisSpec(VariableSchemaSupport, BrowserDefaultMixin, BaseFolder):
    security = ClassSecurityInfo()
    archetype_name = 'AnalysisSpec'
    schema = schema
    allowed_content_types = ()
    content_icon = 'analysisspec.png'
    immediate_view = 'base_view'
    use_folder_tabs = 0
    global_allow = 0
    filter_content_types = 0
    factory_type_information = {
        'title': 'Analysis specification'
    }
    
    actions = (
        { 'id': 'view',
          'name': 'View',
          'action': 'string:${object_url}/',
          'permissions': (permissions.View,),
          'visible': True,
        },
        {'id': 'edit',
         'name': 'Edit',
         'action': 'string:${object_url}/analysisspec_edit',
         'permissions': (ListFolderContents,),
        },
    )


    def Title(self):
        """ Return the SampleType as title """
        try:
            st = self.getSampleType()
            return st and st.Title() or ''
        except:
            return ''


    security.declarePublic('getSpecCategories')
    def getSpecCategories(self): 
        tool = getToolByName(self, REFERENCE_CATALOG)
        categories = []
        for spec in self.getResultsRange():
            uid = spec['service']
            service = tool.lookupObject(spec['service'])
            if service.getCategoryUID() not in categories:
                categories.append(service.getCategoryUID())
        return categories

    security.declarePublic('getResultsRangeDict')
    def getResultsRangeDict(self): 
        specs = {} 
        for spec in self.getResultsRange():
            uid = spec['service']
            specs[uid] = {}
            specs[uid]['min'] = spec['min'] 
            specs[uid]['max'] = spec['max'] 
            specs[uid]['error'] = spec['error'] 
        return specs
             
    security.declarePublic('getResultsRangeSorted')
    def getResultsRangeSorted(self): 
        tool = getToolByName(self, REFERENCE_CATALOG)

        cats = {} 
        for spec in self.getResultsRange():
            service = tool.lookupObject(spec['service'])
            service_title = service.Title()
            category_title = service.getCategoryName()
            if not cats.has_key(category_title):
                 cats[category_title] = {}
            cat = cats[category_title]
            cat[service_title] = {'category': category_title,
                                  'service': service_title,
                                  'id': service.getId(),
                                  'uid': spec['service'],
                                  'min': spec['min'],
                                  'max': spec['max'],
                                  'error': spec['error'] }
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
             

registerType(AnalysisSpec, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] == 'view':
            a['visible'] = 1
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
