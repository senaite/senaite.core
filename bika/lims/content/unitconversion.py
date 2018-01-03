# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims.interfaces import IBikaSetupCatalog
from plone.dexterity.content import Item
from plone.indexer import indexer
from plone.supermodel import model
from zope import schema
from zope.interface import implements

class IUnitConversion(model.Schema):
    """ A Unit Conversion.
    """

    converted_unit = schema.TextLine(
            title=u"Converted Unit",
            description=u"The name of the new converted unit.",
            required=True,
        )

    formula = schema.TextLine(
            title=u"Formula",
            description=u'The formula that is used to convert the unit. Use the keyword "Value" to indicate where the existing result fits into the formula.',
            required=True,
        )



@indexer(IUnitConversion)
def title(obj):
    if obj.title:
        return obj.title


@indexer(IUnitConversion)
def sortable_title(obj):
    if obj.title:
        return [w.lower() for w in obj.title.split(' ')]

class UnitConversion(Item):
    implements(IUnitConversion)

    # Bika catalog multiplex for Dexterity contents
    # please see event handlers in bika.lims.subscribers.catalogobject
    _bika_catalogs = [
        "bika_setup_catalog"
    ]


