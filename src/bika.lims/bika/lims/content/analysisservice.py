"""Definition of the AnalysisService content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from bika.lims.interfaces import IAnalysisService
from bika.lims.config import PROJECTNAME

AnalysisServiceSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AnalysisServiceSchema['title'].storage = atapi.AnnotationStorage()
AnalysisServiceSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(AnalysisServiceSchema, moveDiscussion = False)

class AnalysisService(base.ATCTContent):
    """Analysis Service"""
    implements(IAnalysisService)

    meta_type = "AnalysisService"
    schema = AnalysisServiceSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(AnalysisService, PROJECTNAME)
