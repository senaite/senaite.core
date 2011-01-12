"""ClientFolder is a container for Client instances.

$Id: ClientFolder.py 621 2007-03-16 22:12:30Z anneline $
"""
from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.bika.interfaces import IClientFolder
from Products.bika.config import PROJECTNAME

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit':'hidden', 'view': 'invisible'}
schema['title'].widget.visible = {'edit':'hidden', 'view': 'invisible'}

class ClientFolder(folder.ATFolder):
    implements(IClientFolder)
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(ClientFolder, PROJECTNAME)
