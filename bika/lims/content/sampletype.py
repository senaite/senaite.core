from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.browser.widgets import DurationWidget
from bika.lims.browser.fields import DurationField
from bika.lims.content.bikaschema import BikaSchema
from magnitude import mg
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    DurationField('RetentionPeriod',
        required = 1,
        default_method = 'getDefaultLifetime',
        widget = DurationWidget(
            label = _("Retention period"),
            description = _("The period for which un-preserved samples of this type can be kept before "
                            "they expire and cannot be analysed any further"),
        )
    ),
    BooleanField('Hazardous',
        default = False,
        widget = BooleanWidget(
            label = _("Hazardous"),
            description = _("Samples of this type should be treated as hazardous"),
        ),
    ),
    StringField('Prefix',
        required = True,
        widget = StringWidget(
            label = _('Sample Type Prefix'),
        ),
    ),
    StringField('Unit',
        required = 1,
        widget = StringWidget(
            label = _("Unit"),
            description = _("Sample volume is specified in this unit."),
        ),
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class SampleType(BaseContent, HistoryAwareMixin):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getDefaultLifetime(self):
        """ get the default retention period """
        settings = getToolByName(self, 'bika_setup')
        return settings.getDefaultSampleLifetime()

    def getUnits(self):
        return getUnits(self)

registerType(SampleType, PROJECTNAME)
