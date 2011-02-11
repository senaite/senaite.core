from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
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
    schema = schema

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
