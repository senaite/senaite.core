# -*- coding: utf-8 -*-

from plone.dexterity.content import Container
from plone.supermodel import model
from senaite.core.interfaces import IHideActionsMenu
from senaite.core.interfaces import ISampleContainers
from zope.interface import implementer


class ISampleContainersSchema(model.Schema):
    """Schema interface
    """


@implementer(ISampleContainers, ISampleContainersSchema, IHideActionsMenu)
class SampleContainers(Container):
    """A container for sample containers
    """
