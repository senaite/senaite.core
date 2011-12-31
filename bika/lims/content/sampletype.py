from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IGenerateUniqueId
from bika.lims import bikaMessageFactory as _
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    IntegerField('RetentionPeriod',
        required = 1,
        default_method = 'getDefaultLifetime',
        widget = IntegerWidget(
            label = _("Retention period"),
            description = _("Retention period description",
                            "The period for which Samples of this type can be kept before "
                            "they expire and cannot be analysed any further"),
        )
    ),
    BooleanField('Hazardous',
        default = False,
        widget = BooleanWidget(
            label = _("Hazardous"),
            description = _("Hazardous description",
                            "Samples of this type should be treated as hazardous"),
        ),
    ),
    StringField('Prefix',
        required = True,
        widget = StringWidget(
            label = _('Sample Type Prefix'),
        ),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class SampleType(BaseContent, HistoryAwareMixin):
    implements(IGenerateUniqueId)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def getDefaultLifetime(self):
        """ get the default retention period """
        settings = getToolByName(self, 'bika_setup')
        return settings.getDefaultSampleLifetime()

registerType(SampleType, PROJECTNAME)
