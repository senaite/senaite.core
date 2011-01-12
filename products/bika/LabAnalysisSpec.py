import sys
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.bika.BikaContent import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.bika.CustomFields import AnalysisSpecField

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
    AnalysisSpecField('ResultsRange',
        required = 1,
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
TitleField.widget.visible = False

class LabAnalysisSpec(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'LabAnalysisSpec'
    schema = schema
    allowed_content_types = ()
    default_view = 'labanalysisspec_edit'
    immediate_view = 'labanalysisspec_edit'
    content_icon = 'analysisspec.png'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0

    actions = (
       {'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/labanalysisspec_edit',
        'permissions': (ModifyPortalContent,),
        },
    )

    factory_type_information = {
        'title': 'Lab analysis specification'
    }

    def Title(self):
        st = self.getSampleType()
        return st and st.Title() or ''

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

    security.declarePublic('getCategories')
    def getSpecCategories(self): 
        tool = getToolByName(self, REFERENCE_CATALOG)
        categories = []
        for spec in self.getResultsRange():
            uid = spec['service']
            service = tool.lookupObject(spec['service'])
            if service.getCategoryUID() not in categories:
                categories.append(service.getCategoryUID())
        return categories

    security.declarePublic('getRemainingSampleTypes')
    def getRemainingSampleTypes(self): 
        unavailable_sampletypes = []
        for _as in self.portal_catalog(portal_type = 'LabAnalysisSpec'):
            if _as.UID != self.UID():
                spec = _as.getObject()
                st = spec.getSampleType()
                if st:
                    unavailable_sampletypes.append(st.UID())

        available_sampletypes = []
        for st in self.portal_catalog(portal_type = 'SampleType'):
            if st.UID not in unavailable_sampletypes:
                available_sampletypes.append((st.UID, st.Title))

        return DisplayList(available_sampletypes)

registerType(LabAnalysisSpec, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
