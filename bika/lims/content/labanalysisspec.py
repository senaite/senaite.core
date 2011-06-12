from AccessControl import ClassSecurityInfo
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from bika.lims.browser.fields import SpecField
from bika.lims.browser.widgets import SpecWidget
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
import sys

schema = BikaSchema.copy() + Schema((
    ReferenceField('SampleType',
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SampleType',),
        relationship = 'LabAnalysisSpecSampleType',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Sample Type',
            label_msgid = 'label_type',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    SpecField('ResultsRange',
        required = 1,
        widget = SpecWidget(
            checkbox_bound = 1,
            label = 'Results Range',
            label_msgid = 'label_resultsrange',
            i18n_domain = I18N_DOMAIN,
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

schema['title'].required = False
schema['title'].widget.visible = False

class LabAnalysisSpec(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    schema = schema

    def Title(self):
        st = self.getSampleType()
        return st and st.Title() or ''

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

registerType(LabAnalysisSpec, PROJECTNAME)
