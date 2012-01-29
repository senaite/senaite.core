from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME

schema = BikaSchema.copy() + Schema((
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class ContainerType(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(ContainerType, PROJECTNAME)
