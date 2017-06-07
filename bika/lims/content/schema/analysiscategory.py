# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from sys import maxsize

from Products.Archetypes.Field import FloatField, ReferenceField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import DecimalWidget, ReferenceWidget, \
    TextAreaWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.content.schema.bikaschema import BikaSchema
from bika.lims.content.schema import Storage

Comments = TextField(
    'Comments',
    storage=Storage,
    default_output_type='text/plain',
    allowable_content_types=('text/plain',),
    widget=TextAreaWidget(
        description=_(
            "To be displayed below each Analysis Category section on results "
            "reports."),
        label=_("Comments")
    ),
)

Department = ReferenceField(
    'Department',
    storage=Storage,
    required=1,
    vocabulary='getDepartments',
    vocabulary_display_path_bound=maxsize,
    allowed_types=('Department',),
    relationship='AnalysisCategoryDepartment',
    referenceClass=HoldingReference,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Department"),
        description=_("The laboratory department")
    ),
)

SortKey = FloatField(
    'SortKey',
    storage=Storage,
    validators=('SortKeyValidator',),
    widget=DecimalWidget(
        label=_("Sort Key"),
        description=_(
            "Float value from 0.0 - 1000.0 indicating the sort order. "
            "Duplicate values are ordered alphabetically."),
    ),
)

schema = BikaSchema.copy() + Schema((
    Comments,
    Department,
    SortKey,
))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'
