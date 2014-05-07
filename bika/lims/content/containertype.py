from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
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

    def getContainers(self):
        """Return a list of all containers of this type
        """
        _containers = []
        for container in self.bika_setup.bika_containers.objectValues():
            containertype = container.getContainerType()
            if containertype and containertype.UID() == self.UID():
                _containers.append(container)
        return _containers

registerType(ContainerType, PROJECTNAME)

def ContainerTypes(self, instance=None, allow_blank=False):
    instance = instance or self
    bsc = getToolByName(instance, 'bika_setup_catalog')
    items = []
    for o in bsc(portal_type='ContainerType',
                 sort_on = 'sortable_title'):
        items.append((o.UID, o.Title))
    items = allow_blank and [['','']] + list(items) or list(items)
    return DisplayList(items)
