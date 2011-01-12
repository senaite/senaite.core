from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.bika.BikaContent import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME 
from Products.CMFCore.utils import getToolByName

schema = BikaSchema.copy() + Schema((
    TextField('SampleTypeDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    IntegerField('RetentionPeriod',
        required = 1,
        default_method = 'getDefaultLifetime',
        widget = IntegerWidget(
            label = 'Retention period',
            label_msgid = 'label_retention_period',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    BooleanField('Hazardous',
        default = False,
        widget = BooleanWidget(
            label = "Hazardous",
            label_msgid = "label_hazardous",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))

class SampleType(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'SampleType'
    schema = schema
    allowed_content_types = ()
    immediate_view = 'tool_base_edit'
    default_view = 'tool_base_edit'
    content_icon = 'sampletype.png'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0

    actions = (
       {'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/tool_base_edit',
        'permissions': (ModifyPortalContent,),
        },
    )

    def getDefaultLifetime(self):
        """ get the default retention period """
        settings = getToolByName(self, 'bika_settings').settings
        return settings.getDefaultSampleLifetime()

    factory_type_information = {
        'title': 'Sample type'
    }  

registerType(SampleType, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti

