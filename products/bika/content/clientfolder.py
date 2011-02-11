"""ClientFolder is a container for Client instances.

$Id: ClientFolder.py 621 2007-03-16 22:12:30Z anneline $
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.bika.config import PROJECTNAME
from plone.app.folder import folder
from Products.bika.interfaces import ILims
from zope.interface import implements

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit':'hidden', 'view': 'invisible'}
schema['title'].widget.visible = {'edit':'hidden', 'view': 'invisible'}

class ClientFolder(folder.ATFolder):
    implements(ILims)
    schema = schema
    displayContentsTab = False


schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(ClientFolder, PROJECTNAME)
