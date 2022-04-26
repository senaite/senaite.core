# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import config
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAutoImportLog
from DateTime import DateTime
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import DateTimeField
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import StringField
from Products.Archetypes.public import TextField
from Products.Archetypes.references import HoldingReference
from zope.interface import implements

schema = BikaSchema.copy() + atapi.Schema((

    # Results File that system wanted to import
    StringField(
        "ImportFile",
        default="",
    ),

    ReferenceField(
        "Instrument",
        allowed_types=("Instrument",),
        referenceClass=HoldingReference,
        relationship="InstrumentImportLogs",
    ),

    StringField(
        "Interface",
        default="",
    ),

    TextField(
        "Results",
        default="",
    ),

    DateTimeField(
        "LogTime",
        default=DateTime(),
    ),
))

schema["title"].widget.visible = False


class AutoImportLog(BaseContent):
    """
    This object will have some information/log about auto-import process
    once they are done(failed).
    """
    implements(IAutoImportLog)
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getInstrumentUID(self):
        if self.getInstrument():
            return self.getInstrument().UID()
        return None

    def getInstrumentTitle(self):
        if self.getInstrument():
            return self.getInstrument().Title()
        return None

    def getInstrumentUrl(self):
        if self.getInstrument():
            return self.getInstrument().absolute_url_path()
        return None


# Activating the content type in Archetypes' internal types registry
atapi.registerType(AutoImportLog, config.PROJECTNAME)
