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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from plone.app.blob.field import FileField as BlobFileField
from Products.CMFCore.utils import getToolByName
from senaite.core.content.bikaschema import BikaSchema
from senaite.core.config import PROJECTNAME
from senaite.core import bikaMessageFactory as _
from senaite.core.utils import t
from senaite.core.browser import ulocalized_time
from senaite.core.utils import user_fullname

schema = BikaSchema.copy() + Schema((
    BlobFileField('ReportFile',
        widget = FileWidget(
            label=_("Report"),
        ),
    ),
    StringField('ReportType',
        widget = StringWidget(
            label=_("Report Type"),
            description=_("Report type"),
        ),
    ),
    ReferenceField('Client',
        allowed_types = ('Client',),
        relationship = 'ReportClient',
        widget = ReferenceWidget(
            label=_("Client"),
        ),
    ),
),
)

schema['id'].required = False
schema['title'].required = False

class Report(BaseFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    @security.public
    def getClientUID(self):
        client = self.getClient()
        if client:
            return client.UID()
        return ''

    @security.public
    def getCreatorFullName(self):
        return user_fullname(self, self.Creator())

    @security.public
    def getFileSize(self):
        file = self.getReportFile()
        if file:
            return '%sKb' % (file.get_size() / 1024)
        return ''

    @security.public
    def getClientURL(self):
        client = self.getClient()
        if client:
            return client.absolute_url_path()
        return ''

    @security.public
    def getClientTitle(self):
        client = self.getClient()
        if client:
            return client.Title()
        return ''


atapi.registerType(Report, PROJECTNAME)
