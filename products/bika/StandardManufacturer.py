from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.bika.BikaContent import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME 

schema = BikaSchema.copy() + Schema((
    TextField('StandardManufacturerDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))

class StandardManufacturer(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'StandardManufacturer'
    schema = schema
    allowed_content_types = ()
    immediate_view = 'tool_base_edit'
    default_view = 'tool_base_edit'
    content_icon = 'standardmanufacturer.png'
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

    factory_type_information = {
        'title': 'Standard manufacturer'
    }  

registerType(StandardManufacturer, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti

