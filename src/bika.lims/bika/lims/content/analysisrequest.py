"""Definition of the AnalysisRequest content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-
from bika.lims import limsMessageFactory as _

from bika.lims.interfaces import IAnalysisRequest
from bika.lims.config import PROJECTNAME

AnalysisRequestSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.ReferenceField(
        'analyses',
        storage=atapi.AnnotationStorage(),
        widget=atapi.ReferenceWidget(
            label=_(u"Analyses"),
            description=_(u"Analyses"),
        ),
        required=True,
        relationship='analysisrequest_analyses',
        allowed_types=('Analysis'), # specify portal type names here ('Example Type',)
        multiValued=True,
    ),


    atapi.ReferenceField(
        'samples',
        storage=atapi.AnnotationStorage(),
        widget=atapi.ReferenceWidget(
            label=_(u"Samples"),
            description=_(u"Samples"),
        ),
        required=True,
        relationship='analysisrequest_samples',
        allowed_types=('Sample'), # specify portal type names here ('Example Type',)
        multiValued=True,
    ),


))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

AnalysisRequestSchema['title'].storage = atapi.AnnotationStorage()
AnalysisRequestSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema( AnalysisRequestSchema, folderish=True, moveDiscussion=False )


class AnalysisRequest(folder.ATFolder):
    """Analysis Request"""
    implements(IAnalysisRequest)
    schema = AnalysisRequestSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    analyses = atapi.ATReferenceFieldProperty('analyses')

    samples = atapi.ATReferenceFieldProperty('samples')


atapi.registerType(AnalysisRequest, PROJECTNAME)
