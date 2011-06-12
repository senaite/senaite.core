"""ClientFolder is a container for Client instances.

$Id: ClientFolder.py 621 2007-03-16 22:12:30Z anneline $
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.bika.config import PROJECTNAME
from AccessControl import ClassSecurityInfo
from Products.bika.interfaces import IClientFolder
from plone.app.folder import folder
from Products.bika.utils import generateUniqueId
from zope.interface import implements


schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit':'hidden', 'view': 'invisible'}
schema['title'].widget.visible = {'edit':'hidden', 'view': 'invisible'}

class ClientFolder(folder.ATFolder):
    implements(IClientFolder)
    schema = schema
    security = ClassSecurityInfo()
    displayContentsTab = False

    security.declarePublic('generateUniqueId')
    def generateUniqueId (self, type_name, batch_size = None):
        return generateUniqueId(self, type_name, batch_size)

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(ClientFolder, PROJECTNAME)
