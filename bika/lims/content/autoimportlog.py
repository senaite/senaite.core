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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from zope.interface import implements
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseContent
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims import config
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName


schema = BikaSchema.copy() + atapi.Schema((
    # Results File that system wanted to import
    atapi.StringField('ImportedFile', default=''),

    atapi.ReferenceField('Instrument',
                         allowed_types=('Instrument',),
                         referenceClass=HoldingReference,
                         relationship='InstrumentImportLogs',
                         ),

    atapi.StringField('Interface', default=''),

    atapi.StringField('Results', default=''),

    atapi.DateTimeField('LogTime', default=DateTime()),
))

schema['title'].widget.visible = False


class AutoImportLog(BaseContent):
    """
    This object will have some information/log about auto-import process
    once they are done(failed).
    """
    schema = schema

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
