"""Definition of the Analysis content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.references import HoldingReference

# -*- Message Factory Imported Here -*-
from bika.lims import limsMessageFactory as _

from bika.lims.interfaces import IAnalysis
from bika.lims.config import PROJECTNAME

AnalysisSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.ReferenceField(
        'result',
        storage=atapi.AnnotationStorage(),
        widget=atapi.ReferenceWidget(
            label=_(u"Result Value"),
            description=_(u"Result Value"),
        ),
        relationship='analysis_result',
        allowed_types=('Result'), # specify portal type names here ('Example Type',)
        multiValued=False,
    ),
    atapi.StringField(
        'analysisservice',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Analysis Service"),
            description=_(u"The analysis service"),
        ),
        required=True,
    ),






))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

AnalysisSchema['title'].storage = atapi.AnnotationStorage()
AnalysisSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(AnalysisSchema, moveDiscussion=False)


class Analysis(base.ATCTContent):
    """Analysis"""
    implements(IAnalysis)
    schema = AnalysisSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    result = atapi.ATReferenceFieldProperty('result')

    analysisservice = atapi.ATReferenceFieldProperty('analysisservice')


atapi.registerType(Analysis, PROJECTNAME)

