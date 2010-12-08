"""Interfaces for controlpanel utilities.
"""

from bika.lims import limsMessageFactory as _
from zope import schema
from zope.interface import Interface


class IAnalysisService(Interface):
    """The form schema for a single analysis service object
    """

    title = schema.TextLine(
        title=_(u"Title"),
        required=False,
        description=_(u"Service display name"),
    )
    instructions = schema.TextLine(
        title=_(u"Instructions"),
        required=False,
        description=_(u"Instructions for the actual analysis"),
    )
    unit = schema.TextLine(
        title=_(u"Unit"),
        required=False,
        description=_(u"Unit for entering results"),
    )


class IAnalysisServices(Interface):
    """The Analysis Services form schema.
    """

    title = schema.List(
        title=_(u"Analysis Services"),
        required=False,
        value_type = schema.Object(schema=IAnalysisService),
        description=_(u" "),
    )


