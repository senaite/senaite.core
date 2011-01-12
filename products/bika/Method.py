from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.bika.BikaContent import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME

schema = BikaSchema.copy() + Schema((
    TextField('MethodDescription',
        widget = TextAreaWidget(
            label = 'Method description',
            label_msgid = 'label_method_description',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    FileField('MethodDocument',
        widget = FileWidget(
            label = 'Method document',
            label_msgid = 'label_method_document',
            i18n_domain = I18N_DOMAIN,
        )
    ),
))

class Method(BrowserDefaultMixin, BaseFolder):
    security = ClassSecurityInfo()
    archetype_name = 'Method'
    schema = schema
    allowed_content_types = ('MethodLogEntry',)
    default_view = 'tool_base_edit'
    immediate_view = 'tool_base_edit'
    content_icon = 'method.png'
    global_allow = 0
    filter_content_types = 1
    use_folder_tabs = 0

    actions = (
       {'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/tool_base_edit',
        'permissions': (ModifyPortalContent,),
       },
       {'id': 'log',
        'name': 'Log',
        'action': 'string:${object_url}/method_log',
        'permissions': (View,),
       },
    )

    factory_type_information = {
        'title': 'Method'
    }

    security.declareProtected(ModifyPortalContent, 'create_log_entry')
    def create_log_entry(self):
        """ Create log entry
        """
        entry_id = self.generateUniqueId('MethodLogEntry')
        self.invokeFactory(id = entry_id, type_name = 'MethodLogEntry')

    security.declareProtected(ModifyPortalContent, 'processForm')
    def processForm(self, data = 1, metadata = 0, REQUEST = None, values = None):
        """ Override BaseObject.processForm so that we can create a log entry
        """
        BaseFolder.processForm(self, data = data, metadata = metadata,
            REQUEST = REQUEST, values = values)
        self.create_log_entry()


registerType(Method, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('edit', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
