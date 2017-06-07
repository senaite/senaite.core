# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseContent
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.instrumentlocation import schema
from bika.lims.interfaces import IInstrumentLocation
from zope.interface import implements


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
