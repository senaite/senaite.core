from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
from bika.lims.config import PROJECTNAME, PRESERVATION_CATEGORIES
from bika.lims.content.bikaschema import BikaSchema
import sys

schema = BikaSchema.copy() + Schema((
    StringField('Category',
        default='lab',
        vocabulary=PRESERVATION_CATEGORIES,
        widget=SelectionWidget(
            format='flex',
            label=_('Preservation Category'),
        ),
    ),
    DurationField('RetentionPeriod',
        widget=DurationWidget(
            label=_('Retention Period'),
            description=_('Once preserved, the sample must be disposed of within this time period.  If not specified, the sample type retention period will be used.')
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class Preservation(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(Preservation, PROJECTNAME)
