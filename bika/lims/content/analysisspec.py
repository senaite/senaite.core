"""Analysis result range specifications for a client
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
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.widgets import AnalysisSpecificationWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from types import ListType, TupleType
from zope.interface import implements
import sys
import time

schema = Schema((
    HistoryAwareReferenceField('SampleType',
        schemata = 'Description',
        required = 1,
        vocabulary = "getRemainingSampleTypes",
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SampleType',),
        relationship = 'AnalysisSpecSampleType',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label = _("Sample Type"),
            description = _("If the sample type you are looking for is not listed here, "
                            "a specification for it has been created already. To edit existing, "
                            "specifications, navigate 1 level up and select the specification by "
                            "clicking on the sample type in the list"),
        ),
    ),
    ComputedField('SampleTypeTitle',
        expression = "context.getSampleType() and context.getSampleType().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SampleTypeUID',
        expression = "context.getSampleType() and context.getSampleType().UID() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
)) + \
BikaSchema.copy() + \
Schema((
    RecordsField('ResultsRange',
        schemata = 'Specifications',
        required = 1,
        type = 'analysisspec',
        subfields = ('keyword', 'min', 'max', 'error'),
        required_subfields = ('keyword', 'min', 'max', 'error'),
        subfield_labels = {'keyword': _('Analysis Service'),
                           'min': _('Min'),
                           'max': _('Max'),
                           'error': _('% Error')},
        widget = AnalysisSpecificationWidget(
            checkbox_bound = 1,
            label = _("Specifications"),
            description = _("Click on Analysis Categories (against shaded background) "
                            "to see Analysis Services in each category. Enter minimum "
                            "and maximum values to indicate a valid results range. "
                            "Any result outside this range will raise an alert. "
                            "The % Error field allows for an % uncertainty to be "
                            "considered when evaluating results against minimum and "
                            "maximum values. A result out of range but still in range "
                            "if the % error is taken into consideration, will raise a "
                            "less severe alert."),
        ),
    ),
    ComputedField('ClientUID',
        expression = "context.aq_parent.UID()",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
))
schema['description'].schemata = 'Description'
schema['description'].widget.visible = True
schema['title'].schemata = 'Description'
schema['title'].required = False
schema['title'].widget.visible = False

class AnalysisSpec(BaseFolder, HistoryAwareMixin):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the SampleType as title """
        try:
            st = self.getSampleType()
            return st and st.Title() or ''
        except:
            return ''

    security.declarePublic('getSpecCategories')
    def getSpecCategories(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        categories = []
        for spec in self.getResultsRange():
            keyword = spec['keyword']
            service = bsc(portal_type="AnalysisService",
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
            category_title = service.getCategoryTitle()
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
        bsc = getToolByName(self, 'bika_setup_catalog')
        for st in bsc(portal_type = 'SampleType',
                      sort_on = 'sortable_title'):
            if st.UID not in unavailable_sampletypes:
                available_sampletypes.append((st.UID, st.Title))

        return DisplayList(available_sampletypes)

atapi.registerType(AnalysisSpec, PROJECTNAME)
