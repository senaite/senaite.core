# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema
from plone.app.blob.field import FileField

DocumentID = atapi.StringField(
    'DocumentID',
    storage=Storage(),
    required=1,
    validators=('uniquefieldvalidator',),
    widget=atapi.StringWidget(
        label=_("Document ID")
    ),
)

File = FileField(
    'File',
    storage=Storage(),
    required=1,
    widget=atapi.FileWidget(
        label=_("Document"),
        description=_("File upload ")
    ),
)

DocumentVersion = atapi.StringField(
    'DocumentVersion',
    storage=Storage(),
    widget=atapi.StringWidget(
        label=_("Document Version")
    ),
)

DocumentLocation = atapi.StringField(
    'DocumentLocation',
    storage=Storage(),
    widget=atapi.StringWidget(
        label=_("Document Location"),
        description=_("Location where the document set is shelved")
    ),
)

DocumentType = atapi.StringField(
    'DocumentType',
    storage=Storage(),
    required=1,
    widget=atapi.StringWidget(
        label=_("Document Type"),
        description=_(
            "Type of document (e.g. user manual, instrument specifications, "
            "image, ...)")
    ),
)

schema = BikaSchema.copy() + atapi.Schema((
    DocumentID,
    File,
    DocumentVersion,
    DocumentLocation,
    DocumentType
))

TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = False
