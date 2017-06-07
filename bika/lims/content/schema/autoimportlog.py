# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from DateTime import DateTime
from Products.Archetypes.Field import DateTimeField, ReferenceField, StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.references import HoldingReference
from bika.lims.content.schema.bikaschema import BikaSchema
from bika.lims.content.schema import Storage

# Results File that system wanted to import
ImportedFile = StringField('ImportedFile', default='')

Instrument = ReferenceField(
    'Instrument',
    storage=Storage,
    allowed_types=('Instrument',),
    referenceClass=HoldingReference,
    relationship='InstrumentImportLogs',
)

Interface = StringField(
    'Interface',
    storage=Storage,
    default='',
)

Results = StringField(
    'Results',
    storage=Storage,
    default='',
)

LogTime = DateTimeField(
    'LogTime',
    storage=Storage,
    default=DateTime(),
)

schema = BikaSchema.copy() + Schema((
    ImportedFile,
    Instrument,
    Interface,
    Results,
    LogTime
))

schema['title'].widget.visible = False
