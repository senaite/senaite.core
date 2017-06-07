# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from plone.app.blob.field import FileField as BlobFileField

ReportFile = BlobFileField(
    'ReportFile',
    widget=FileWidget(
        label=_("Report")
    )
)
ReportType = StringField(
    'ReportType',
    widget=StringWidget(
        label=_("Report Type"),
        description=_("Report type")
    )
)
Client = ReferenceField(
    'Client',
    allowed_types=('Client',),
    relationship='ReportClient',
    widget=ReferenceWidget(
        label=_("Client")
    )
)

schema = BikaSchema.copy() + Schema((
    ReportFile,
    ReportType,
    Client
))

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

    def getClientUID(self):
        client = self.getClient()
        if client:
            return client.UID()
        return ''


atapi.registerType(Report, PROJECTNAME)
