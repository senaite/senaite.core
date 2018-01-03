# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from plone.app.blob.field import FileField as BlobFileField
from Products.CMFCore.utils import getToolByName
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser import ulocalized_time
from bika.lims.utils import user_fullname

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
        from bika.lims.idserver import renameAfterCreation
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
