# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import ReferenceField, StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import FileWidget, ReferenceWidget, StringWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema
from plone.app.blob.field import FileField as BlobFileField

ReportFile = BlobFileField(
    'ReportFile',
    storage=Storage,
    widget=FileWidget(
        label=_("Report")
    ),
)

ReportType = StringField(
    'ReportType',
    storage=Storage,
    widget=StringWidget(
        label=_("Report Type"),
        description=_("Report type")
    ),
)

Client = ReferenceField(
    'Client',
    storage=Storage,
    allowed_types=('Client',),
    relationship='ReportClient',
    widget=ReferenceWidget(
        label=_("Client")
    ),
)

schema = BikaSchema.copy() + Schema((
    ReportFile,
    ReportType,
    Client
))

schema['id'].required = False
schema['title'].required = False
