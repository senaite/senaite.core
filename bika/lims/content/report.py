# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.utils import user_fullname
from plone.app.blob.field import FileField as BlobFileField

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
    UIDReferenceField('Client',
        allowed_types = ('Client',),
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
