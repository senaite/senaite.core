"""Supply Order Folder contains Supply Orders
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
from AccessControl import ClassSecurityInfo
from bika.lims.interfaces import ISupplyOrderFolder, IHaveNoBreadCrumbs
from plone.app.folder import folder
from zope.interface import implements

schema = folder.ATFolderSchema.copy()


class SupplyOrderFolder(folder.ATFolder):
    implements(ISupplyOrderFolder, IHaveNoBreadCrumbs)
    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(SupplyOrderFolder, PROJECTNAME)
