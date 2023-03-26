# -*- coding: utf-8 -*-

from plone.supermodel import model
from senaite.core.content.base import Container
from senaite.core.interfaces import IHideActionsMenu
from senaite.core.interfaces import ILabels
from zope.interface import implementer


class ILabelsSchema(model.Schema):
    """Schema interface
    """


@implementer(ILabels, ILabelsSchema, IHideActionsMenu)
class Labels(Container):
    """A container for labels
    """
