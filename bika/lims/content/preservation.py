from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME, PRESERVATION_CATEGORIES

schema = BikaSchema.copy() + Schema((
    StringField('Category',
        default='lab',
        vocabulary=PRESERVATION_CATEGORIES,
        widget=SelectionWidget(
            format='flex',
            label=_('Preservation Category'),
        ),
    ),
    DurationField('MaxHoldingTime',
        widget=DurationWidget(
            label=_('Maximum holding time'),
            description=_('Maximum holding time description',
                          'Once preserved, the sample must be disposed of within this time period')
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
