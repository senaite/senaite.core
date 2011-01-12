from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.bika.BikaContent import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME 
from Products.bika.CustomFields import TemplatePositionField
from Products.bika.config import ANALYSIS_TYPES

schema = BikaSchema.copy() + Schema((
    TextField('WorksheetTemplateDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    TemplatePositionField('Row',
        required = 1,
    ),
    ReferenceField('Service',
        required = 1,
        multiValued = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'WorksheetTemplateAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = 'Analysis service',
            label_msgid = 'label_analysis',
            i18n_domain = I18N_DOMAIN,
        )
    ),
))

class WorksheetTemplate(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'WorksheetTemplate'
    schema = schema
    allowed_content_types = ()
    immediate_view = 'worksheettemplate_edit'
    default_view = 'worksheettemplate_edit'
    content_icon = 'worksheettemplate.png'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0


    actions = (
       {'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/worksheettemplate_edit',
        'permissions': (ModifyPortalContent,),
        },
    )

    factory_type_information = {
        'title': 'Worksheet Template'
    }  

    security.declarePublic('getAnalysisTypes')
    def getAnalysisTypes(self):
        """ return Analysis type displaylist """
        return ANALYSIS_TYPES()

registerType(WorksheetTemplate, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
