# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import BooleanField, FixedPointField, \
    StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DecimalWidget, SelectionWidget
from bika.lims.config import PRICELIST_TYPES
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaFolderSchema

Type = StringField(
    'Type',
    storage=Storage,
    required=1,
    vocabulary=PRICELIST_TYPES,
    widget=SelectionWidget(
        format='select',
        label=_("Pricelist for")
    ),
)

BulkDiscount = BooleanField(
    'BulkDiscount',
    storage=Storage,
    default=False,
    widget=SelectionWidget(
        label=_("Bulk discount applies")
    ),
)

BulkPrice = FixedPointField(
    'BulkPrice',
    storage=Storage,
    widget=DecimalWidget(
        label=_("Discount %"),
        description=_("Enter discount percentage value")
    ),
)

Descriptions = BooleanField(
    'Descriptions',
    storage=Storage,
    default=False,
    widget=BooleanWidget(
        label=_("Include descriptions"),
        description=_("Select if the descriptions should be included")
    ),
)

Remarks = TextField(
    'Remarks',
    storage=Storage,
    searchable=True,
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_("Remarks"),
        append_only=True
    ),
)

schema = BikaFolderSchema.copy() + Schema((
    Type,
    BulkDiscount,
    BulkPrice,
    Descriptions,
    Remarks
))

Field = schema['title']
Field.required = 1
Field.widget.visible = True

Field = schema['effectiveDate']
Field.schemata = 'default'
Field.required = 0  # "If no date is selected the item will be published
# immediately."
Field.widget.visible = True

Field = schema['expirationDate']
Field.schemata = 'default'
Field.required = 0  # "If no date is chosen, it will never expire."
Field.widget.visible = True
