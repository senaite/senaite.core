# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DateTimeField, UIDReferenceField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema
from plone.app.blob.field import BlobField

AnalysisRequest = UIDReferenceField(
    'AnalysisRequest',
    storage=Storage,
    allowed_types=('AnalysisRequest',),
    referenceClass=HoldingReference,
    required=1,
)

Pdf = BlobField(
    'Pdf',
    storage=Storage,
)

SMS = StringField(
    'SMS',
    storage=Storage,
)

Recipients = RecordsField(
    'Recipients',
    storage=Storage,
    type='recipients',
    subfields=(
        'UID', 'Username', 'Fullname', 'EmailAddress',
        'PublicationModes'),
)

DatePrinted = DateTimeField(
    'DatePrinted',
    storage=Storage,
    mode="rw",
    widget=DateTimeWidget(
        label=_("Date Printed"),
        visible={'edit': 'visible',
                 'view': 'visible'
                 }
    ),
)

schema = BikaSchema.copy() + Schema((
    AnalysisRequest,
    Pdf,
    SMS,
    Recipients,
    DatePrinted
))

schema['id'].required = False
schema['title'].required = False
