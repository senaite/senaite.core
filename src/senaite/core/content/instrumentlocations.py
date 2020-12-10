# -*- coding: utf-8 -*-

from plone.dexterity.content import Container
from plone.supermodel import model
from senaite.core.interfaces import IHideActionsMenu
from zope.interface import implementer


class IInstrumentLocations(model.Schema):
    """Schema and marker interface
    """


@implementer(IInstrumentLocations, IHideActionsMenu)
class InstrumentLocations(Container):
    """A container for instrument locations
    """
