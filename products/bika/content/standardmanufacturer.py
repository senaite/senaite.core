from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
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
    schema = schema

registerType(StandardManufacturer, PROJECTNAME)
