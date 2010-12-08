"""Definition of the Contact content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from bika.lims.interfaces import IContact
from bika.lims.config import PROJECTNAME

ContactSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

ContactSchema['title'].storage = atapi.AnnotationStorage()
ContactSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(ContactSchema, moveDiscussion=False)


class Contact(base.ATCTContent):
    """Contact"""
    implements(IContact)
    schema = ContactSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Contact, PROJECTNAME)
