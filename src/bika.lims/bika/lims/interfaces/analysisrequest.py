from zope.interface import Interface
# -*- Additional Imports Here -*-
from zope import schema

from bika.lims import limsMessageFactory as _


class IAnalysisRequest(Interface):
    """Analysis Request"""

    # -*- schema definition goes here -*-
    analyses = schema.Object(
        title=_(u"Analyses"),
        required=True,
        description=_(u"Analyses"),
        schema=Interface, # specify the interface(s) of the addable types here
    )
#
    samples = schema.Object(
        title=_(u"Samples"),
        required=True,
        description=_(u"Samples"),
        schema=Interface, # specify the interface(s) of the addable types here
    )
#
