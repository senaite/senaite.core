"""Definition of the Client content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from bika.lims.interfaces import IClient
from bika.lims.config import PROJECTNAME

ClientSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ClientSchema['title'].storage = atapi.AnnotationStorage()
ClientSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    ClientSchema,
    folderish=True,
    moveDiscussion=False
)


class Client(folder.ATFolder):
    """Client"""
    implements(IClient)
    schema = ClientSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Client, PROJECTNAME)
