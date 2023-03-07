# -*- coding: utf-8 -*-

from bika.lims import senaiteMessageFactory as _
from plone.autoform import directives
from plone.supermodel import model
from senaite.core.content.base import Container
from senaite.core.interfaces import IHideActionsMenu
from senaite.core.interfaces import ILabel
from senaite.core.schema import UIDReferenceField
from zope import schema
from zope.interface import implementer


class ILabelSchema(model.Schema):
    """Schema interface
    """
    title = schema.TextLine(
        title=u"Title",
        required=False,
    )

    description = schema.Text(
        title=u"Description",
        required=False,
    )

    directives.omitted("labeled")
    labeled = UIDReferenceField(
        title=_(u"Labeled objects"),
        multi_valued=True,
        description=_(u"Objects that are marked with this label"),
        required=False,
    )

    category = schema.TextLine(
        title=u"Category",
        required=False,
    )


@implementer(ILabel, ILabelSchema, IHideActionsMenu)
class Label(Container):
    """A container for labels
    """
