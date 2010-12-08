from zope.interface import Interface
# -*- Additional Imports Here -*-
from zope import schema

from bika.lims import limsMessageFactory as _


class IResult(Interface):
    """Result"""

    # -*- schema definition goes here -*-
    result_value = schema.Text(
        title=_(u"Result Value"),
        required=True,
        description=_(u"Field description"),
    )
#
    result_type = schema.TextLine(
        title=_(u"Result Type"),
        required=True,
        description=_(u"Possible values are defined in Analysis Services"),
    )
#
