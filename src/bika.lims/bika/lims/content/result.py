"""Definition of the Result content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.references import HoldingReference

# -*- Message Factory Imported Here -*-
from bika.lims import limsMessageFactory as _

from bika.lims.interfaces import IResult
from bika.lims.config import PROJECTNAME

ResultSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.TextField(
        'result_value',
        storage=atapi.AnnotationStorage(),
        widget=atapi.TextAreaWidget(
            label=_(u"Result Value"),
            description=_(u"Field description"),
        ),
        required=True,
    ),


    atapi.StringField(
        'result_type',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Result Type"),
            description=_(u"Possible values are defined in Analysis Services"),
        ),
        required=True,
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

ResultSchema['title'].storage = atapi.AnnotationStorage()
ResultSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(ResultSchema, moveDiscussion=False)


class Result(base.ATCTContent):
    """Result"""
    implements(IResult)
    schema = ResultSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    result_value = atapi.ATFieldProperty('result_value')

    result_type = atapi.ATFieldProperty('result_type')


atapi.registerType(Result, PROJECTNAME)
