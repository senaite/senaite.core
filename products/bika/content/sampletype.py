from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.bika.content.bikaschema import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME

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
    schema = schema

    def getDefaultLifetime(self):
        """ get the default retention period """
        settings = getToolByName(self, 'bika_settings').settings
        return settings.getDefaultSampleLifetime()

registerType(SampleType, PROJECTNAME)
