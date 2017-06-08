# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import StringField
from Products.Archetypes.Schema import Schema
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget, SelectionWidget
from bika.lims.config import PRESERVATION_CATEGORIES
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

Category = StringField(
    'Category',
    storage=Storage(),
    default='lab',
    vocabulary=PRESERVATION_CATEGORIES,
    widget=SelectionWidget(
        format='flex',
        label=_("Preservation Category")
    ),
)

RetentionPeriod = DurationField(
    'RetentionPeriod',
    storage=Storage(),
    widget=DurationWidget(
        label=_("Retention Period"),
        description=_(
            'Once preserved, the sample must be disposed of within this time '
            'period.  If not specified, the sample type retention period will '
            'be used.')
    ),
)

schema = BikaSchema.copy() + Schema((
    Category,
    RetentionPeriod
))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'
