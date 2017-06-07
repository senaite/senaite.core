# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import ComputedField, FixedPointField, \
    StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import ComputedWidget, DecimalWidget, \
    StringWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

Volume = StringField(
    'Volume',
    storage=Storage,
    widget=StringWidget(
        label=_("Volume")
    ),
)

Unit = StringField(
    'Unit',
    storage=Storage,
    widget=StringWidget(
        label=_("Unit")
    ),
)

VAT = FixedPointField(
    'VAT',
    storage=Storage,
    default_method='getDefaultVAT',
    widget=DecimalWidget(
        label=_("VAT %"),
        description=_("Enter percentage value eg. 14.0")
    ),
)

Price = FixedPointField(
    'Price',
    storage=Storage,
    required=1,
    widget=DecimalWidget(
        label=_("Price excluding VAT")
    ),
)

VATAmount = ComputedField(
    'VATAmount',
    storage=Storage,
    expression='context.getVATAmount()',
    widget=ComputedWidget(
        label=_("VAT"),
        visible={'edit': 'hidden', }
    ),
)

TotalPrice = ComputedField(
    'TotalPrice',
    storage=Storage,
    expression='context.getTotalPrice()',
    widget=ComputedWidget(
        label=_("Total price"),
        visible={'edit': 'hidden'}
    ),
)

schema = BikaSchema.copy() + Schema((
    Volume,
    Unit,
    VAT,
    Price,
    VATAmount,
    TotalPrice
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True
