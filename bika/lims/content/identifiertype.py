from AccessControl import ClassSecurityInfo
from Products.Archetypes import listTypes
from Products.Archetypes.Field import LinesField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import PicklistWidget
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType
from Products.CMFCore.utils import getToolByName
from bika.lims import PROJECTNAME, bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IHaveIdentifiers

PortalTypes = LinesField(
    'PortalTypes',
    vocabulary='getPortalTypes',
    widget=PicklistWidget(
        label=_("Portal Types"),
        description=_("Select the types that this ID is used to identify."),
    ),
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

    def getPortalTypes(self):
        # cargoed from ArchetypeTool.listPortalTypesWithInterfaces because
        # portal_factory is given a FauxArchetypeTool without this method
        pt = getToolByName(self, 'portal_types')
        value = []
        for data in listTypes():
            klass = data['klass']
            for iface in [IHaveIdentifiers]:
                if iface.implementedBy(klass):
                    ti = pt.getTypeInfo(data['portal_type'])
                    if ti is not None:
                        value.append(ti)
        return [v.Title() for v in value]


registerType(IdentifierType, PROJECTNAME)
