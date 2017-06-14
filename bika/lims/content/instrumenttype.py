# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.instrumenttype import schema
from bika.lims.interfaces import IInstrumentType
from zope.interface import implements


class InstrumentType(BaseContent):
    implements(IInstrumentType)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(InstrumentType, PROJECTNAME)
