# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import DateTimeField, StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import FileWidget, ReferenceWidget, StringWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema
from plone.app.blob.field import FileField

# It comes from blob
AttachmentFile = FileField(
    'AttachmentFile',
    storage=Storage(),
    widget=FileWidget(
        label=_("Attachment")
    ),
)

AttachmentType = UIDReferenceField(
    'AttachmentType',
    storage=Storage(),
    required=0,
    allowed_types=('AttachmentType',),
    widget=ReferenceWidget(
        label=_("Attachment Type")
    ),
)

AttachmentKeys = StringField(
    'AttachmentKeys',
    storage=Storage(),
    searchable=True,
    widget=StringWidget(
        label=_("Attachment Keys")
    ),
)

DateLoaded = DateTimeField(
    'DateLoaded',
    storage=Storage(),
    required=1,
    default_method='current_date',
    widget=DateTimeWidget(
        label=_("Date Loaded")
    ),
)

schema = BikaSchema.copy() + Schema((
    AttachmentFile,
    AttachmentType,
    AttachmentKeys,
    DateLoaded
))

schema['id'].required = False
schema['title'].required = False
