"""ClientFolder is a container for Client instances.

$Id: ClientFolder.py 621 2007-03-16 22:12:30Z anneline $
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.bika.config import PROJECTNAME
from Products.bika.interfaces import IClientFolder
from plone.app.folder import folder
from zope.interface import implements

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit':'hidden', 'view': 'invisible'}
schema['title'].widget.visible = {'edit':'hidden', 'view': 'invisible'}

class ClientFolder(folder.ATFolder):
    implements(IClientFolder)
    schema = schema

    displayContentsTab = False

    def getFolderContents(self, contentFilter):
        portal_catalog = getToolByName(self, 'portal_catalog')
        return portal_catalog(portal_type = 'Client')

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(ClientFolder, PROJECTNAME)
