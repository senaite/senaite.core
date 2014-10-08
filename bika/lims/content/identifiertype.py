from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import LinesField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import MultiSelectionWidget
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME

PortalTypes = LinesField(
    'PortalTypes',
    widget=MultiSelectionWidget(
        label = _("Portal Types"),
        description = _("Select the types that this ID is used to identify")
    )
)

schema = BikaSchema.copy() + Schema((
    PortalTypes,
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class IdentifierType(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(IdentifierType, PROJECTNAME)
