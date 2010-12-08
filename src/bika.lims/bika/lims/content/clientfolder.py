"""Definition of the ClientFolder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from bika.lims.interfaces import IClientFolder
from bika.lims.config import PROJECTNAME

ClientFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ClientFolderSchema['title'].storage = atapi.AnnotationStorage()
ClientFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema( ClientFolderSchema, folderish=True, moveDiscussion=False )


class ClientFolder(folder.ATFolder):
    """Client Folder"""
    implements(IClientFolder)
    schema = ClientFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(ClientFolder, PROJECTNAME)
