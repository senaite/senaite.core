# -*- coding:utf-8 -*-

from sys import maxint

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import IntegerField, ReferenceField, \
    StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import TextAreaWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import IntegerWidget, ReferenceWidget, \
    SRTemplateARTemplatesWidget, SelectionWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

# The default sampler for the rounds
Sampler = StringField(
    'Sampler',
    storage=Storage(),
    required=1,
    searchable=True,
    vocabulary='_getSamplersDisplayList',
    widget=SelectionWidget(
        format='select',
        label=_("Sampler")
    )
)

# The department responsible for the sampling round
Department = ReferenceField(
    'Department',
    storage=Storage(),
    required=1,
    vocabulary_display_path_bound=maxint,
    allowed_types=('Department',),
    vocabulary='_getDepartmentsDisplayList',
    relationship='SRTemplateDepartment',
    referenceClass=HoldingReference,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Department"),
        description=_("The laboratory department"),
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'}
    )
)

# The number of days between recurring field trips
SamplingDaysFrequency = IntegerField(
    'SamplingDaysFrequency',
    storage=Storage(),
    required=1,
    default=7,
    widget=IntegerWidget(
        label=_("Sampling Frequency"),
        description=_(
            "The number of days between recurring field trips")
    )
)

Instructions = TextField(
    'Instructions',
    storage=Storage(),
    searchable=True,
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        label=_("Instructions"),
        append_only=False
    )
)

ARTemplates = ReferenceField(
    'ARTemplates',
    storage=Storage(),
    schemata='AR Templates',
    required=1,
    multiValued=1,
    allowed_types=('ARTemplate',),
    relationship='SRTemplateARTemplate',
    widget=SRTemplateARTemplatesWidget(
        label=_("AR Templates"),
        description=_("Select AR Templates to include")
    )
)

schema = BikaSchema.copy() + Schema((
    Sampler,
    Department,
    SamplingDaysFrequency,
    Instructions,
    ARTemplates
))

schema['description'].widget.visible = True
schema['title'].widget.visible = True
schema['title'].validators = ('uniquefieldvalidator',)
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()
