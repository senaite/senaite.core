"""Analysis result range specifications for a client

$Id: AnalysisSpec.py 443 2006-12-13 23:19:39Z anneline $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import delete_objects
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.field.records import RecordsField
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.utils import shasattr
from Products.CMFCore import permissions
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import ListFolderContents, View
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.widgets import SpecWidget
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from types import ListType, TupleType
import sys
import time
from bika.lims import bikaMessageFactory as _

schema = Schema((
    HistoryAwareReferenceField('SampleType',
        required = 1,
        vocabulary = "getRemainingSampleTypes",
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SampleType',),
        relationship = 'AnalysisSpecSampleType',
        referenceClass = HoldingReference,
    ),
)) + \
BikaSchema.copy() + \
Schema((
    RecordsField('ResultsRange',
        required = 1,
        type = 'analysisspec',
        subfields = ('keyword', 'min', 'max', 'error'),
        required_subfields = ('keyword', 'min', 'max', 'error'),
        subfield_labels = {'keyword': _('Analysis Service'),
                           'min': _('Min'),
                           'max': _('Max'),
                           'error': _('% Error')},
        widget = SpecWidget(
            checkbox_bound = 1,
            label = 'Results Range',
            label_msgid = 'label_resultsrange',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ComputedField('ClientUID',
        index = 'FieldIndex',
        expression = "here.aq_parent.portal_type == 'Client'"+\
                     "and here.aq_parent.UID() or None",
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
schema['description'].schemata = 'default'
schema['description'].widget.visible = True
schema['title'].required = False
schema['title'].widget.visible = False

class AnalysisSpec(BaseFolder, HistoryAwareMixin):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

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
            keyword = spec['keyword']
            service = pc(portal_type="AnalysisService",
                         getKeyword = keyword)
            if service.getCategoryUID() not in categories:
                categories.append(service.getCategoryUID())
        return categories

    security.declarePublic('getResultsRangeDict')
    def getResultsRangeDict(self):
        specs = {}
        for spec in self.getResultsRange():
            keyword = spec['keyword']
            specs[keyword] = {}
            specs[keyword]['min'] = spec['min']
            specs[keyword]['max'] = spec['max']
            specs[keyword]['error'] = spec['error']
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

    security.declarePublic('getRemainingSampleTypes')
    def getRemainingSampleTypes(self):
        """ return all unused sample types """
        """ plus the current object's sample type, if any """
        unavailable_sampletypes = []
        for spec in self.aq_parent.objectValues('AnalysisSpec'):
            st = spec.getSampleType()
            own_sampletype = self.getSampleType() and \
                           self.getSampleType().UID()
            if not st.UID() == own_sampletype:
                unavailable_sampletypes.append(st.UID())

        available_sampletypes = []
        for st in self.portal_catalog(portal_type = 'SampleType',
                                      sort_on = 'sortable_title'):
            if st.UID not in unavailable_sampletypes:
                available_sampletypes.append((st.UID, st.Title))

        return DisplayList(available_sampletypes)

atapi.registerType(AnalysisSpec, PROJECTNAME)
