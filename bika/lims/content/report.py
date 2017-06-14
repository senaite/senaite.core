# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseFolder import BaseFolder
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.report import schema


class Report(BaseFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()

    def getClientUID(self):
        client = self.getClient()
        if client:
            return client.UID()
        return ''


registerType(Report, PROJECTNAME)
