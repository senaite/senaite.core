# -*- coding: utf-8 -*-

from bika.lims.catalog import SETUP_CATALOG
from plone.dexterity.content import Item
from plone.supermodel import model
from zope.interface import implementer


class IInstrumentLocation(model.Schema):
    """Schema and marker interface
    """


@implementer(IInstrumentLocation)
class InstrumentLocation(Item):
    """Holds information about an instrument location
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]
