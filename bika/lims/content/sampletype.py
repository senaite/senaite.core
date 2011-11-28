from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('bika')

schema = BikaSchema.copy() + Schema((
    IntegerField('RetentionPeriod',
        required = 1,
        default_method = 'getDefaultLifetime',
        widget = IntegerWidget(
            label = _("Retention period"),
            description = _("The period for which Samples of this type can be kept before "
                            "they expire and cannot be analysed any further"),
        )
    ),
    BooleanField('Hazardous',
        default = False,
        widget = BooleanWidget(
            label = _("Hazardous"),
            description = _("Check this box if samples of this type should be treated as hazardous"),
        ),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class SampleType(BaseContent, HistoryAwareMixin):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def getDefaultLifetime(self):
        """ get the default retention period """
        settings = getToolByName(self, 'bika_setup')
        return settings.getDefaultSampleLifetime()

registerType(SampleType, PROJECTNAME)
