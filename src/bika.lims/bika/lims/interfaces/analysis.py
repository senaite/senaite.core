from zope.interface import Interface
# -*- Additional Imports Here -*-
from zope import schema

from bika.lims import limsMessageFactory as _


class IAnalysis(Interface):
    """Analysis"""

    # -*- schema definition goes here -*-
    result = schema.Object(
        title=_(u"Result Value"),
        required=False,
        description=_(u"Result Value"),
        schema=Interface, # specify the interface(s) of the addable types here
    )
#
    analysisservice = schema.Object(
        title=_(u"Analysis Service"),
        required=True,
        description=_(u"Analysis Service"),
        schema=Interface, # specify the interface(s) of the addable types here
    )
#
