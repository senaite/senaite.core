# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import implements

from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import BaseContent
from Products.Archetypes import atapi

from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IInstrumentLocation


schema = BikaSchema.copy()

schema['description'].schemata = 'default'
schema['description'].widget.visible = True


class InstrumentLocation(BaseContent):
    """A physical place, where an Instrument is located
    """
    implements(IInstrumentLocation)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

atapi.registerType(InstrumentLocation, PROJECTNAME)
