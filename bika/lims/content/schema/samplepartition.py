# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import BooleanField, ComputedField, \
    DateTimeField, ReferenceField, StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import ComputedWidget
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.content.schema.bikaschema import BikaSchema
from bika.lims.content.schema import Storage

Container = ReferenceField(
    'Container',
    storage=Storage,
    allowed_types=('Container',),
    relationship='SamplePartitionContainer',
    required=1,
    multiValued=0,
)

Preservation = ReferenceField(
    'Preservation',
    storage=Storage,
    allowed_types=('Preservation',),
    relationship='SamplePartitionPreservation',
    required=0,
    multiValued=0,
)

Separate = BooleanField(
    'Separate',
    storage=Storage,
    default=False,
)

Analyses = UIDReferenceField(
    'Analyses',
    storage=Storage,
    allowed_types=('Analysis',),
    required=0,
    multiValued=1,
)

DatePreserved = DateTimeField(
    'DatePreserved',
    storage=Storage,
)

Preserver = StringField(
    'Preserver',
    storage=Storage,
    searchable=True,
)

RetentionPeriod = DurationField(
    'RetentionPeriod',
    storage=Storage,
)

DisposalDate = ComputedField(
    'DisposalDate',
    storage=Storage,
    expression='context.disposal_date()',
    widget=ComputedWidget(
        visible=False
    ),
)

schema = BikaSchema.copy() + Schema((
    Container,
    Preservation,
    Separate,
    Analyses,
    DatePreserved,
    Preserver,
    RetentionPeriod,
    DisposalDate
))

schema['title'].required = False
