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

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from plone.app.blob.field import FileField as BlobFileField
from Products.Archetypes import atapi
from Products.Archetypes.BaseFolder import BaseFolder
from Products.Archetypes.Field import StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import FileWidget
from Products.Archetypes.Widget import StringWidget

from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.clientawaremixin import ClientAwareMixin
from bika.lims.utils import user_fullname


schema = BikaSchema.copy() + Schema((
    BlobFileField(
        "ReportFile",
        widget=FileWidget(
            visible=False,
        ),
    ),
    StringField(
        "ReportType",
        widget=StringWidget(
            visible=False,
        ),
    ),
    UIDReferenceField(
        "Client",
        allowed_types=("Client",),
        widget=ReferenceWidget(
            visible=False,
        ),
    ),
),
)

schema['id'].required = False
schema['title'].required = False


class Report(BaseFolder, ClientAwareMixin):
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

    @security.public
    def getCreatorFullName(self):
        return user_fullname(self, self.Creator())

    @security.public
    def getFileSize(self):
        file = self.getReportFile()
        if file:
            return '%sKb' % (file.get_size() / 1024)
        return ''

atapi.registerType(Report, PROJECTNAME)
