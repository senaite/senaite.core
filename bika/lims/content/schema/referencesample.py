# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""ReferenceSample represents a reference sample used for quality control 
testing
"""
from Products.Archetypes.Field import BooleanField, ComputedField, \
    DateTimeField, ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, ComputedWidget, \
    StringWidget, TextAreaWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import ReferenceResultsField
from bika.lims.browser.widgets import DateTimeWidget as bika_DateTimeWidget, \
    ReferenceWidget
from bika.lims.browser.widgets import ReferenceResultsWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

ReferenceDefinition = ReferenceField(
    'ReferenceDefinition',
    storage=Storage(),
    schemata='Description',
    allowed_types=('ReferenceDefinition',),
    relationship='ReferenceSampleReferenceDefinition',
    referenceClass=HoldingReference,
    vocabulary="getReferenceDefinitions",
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Reference Definition")
    ),
)

Blank = BooleanField(
    'Blank',
    storage=Storage(),
    schemata='Description',
    default=False,
    widget=BooleanWidget(
        label=_("Blank"),
        description=_("Reference sample values are zero or 'blank'")
    ),
)

Hazardous = BooleanField(
    'Hazardous',
    storage=Storage(),
    schemata='Description',
    default=False,
    widget=BooleanWidget(
        label=_("Hazardous"),
        description=_("Samples of this type should be treated as hazardous")
    ),
)

Manufacturer = ReferenceField(
    'Manufacturer',
    storage=Storage(),
    schemata='Description',
    allowed_types=('Manufacturer',),
    relationship='ReferenceSampleManufacturer',
    vocabulary="getManufacturers",
    referenceClass=HoldingReference,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Manufacturer")
    ),
)

CatalogueNumber = StringField(
    'CatalogueNumber',
    storage=Storage(),
    schemata='Description',
    widget=StringWidget(
        label=_("Catalogue Number")
    ),
)

LotNumber = StringField(
    'LotNumber',
    storage=Storage(),
    schemata='Description',
    widget=StringWidget(
        label=_("Lot Number")
    ),
)

Remarks = TextField(
    'Remarks',
    storage=Storage(),
    schemata='Description',
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

DateSampled = DateTimeField(
    'DateSampled',
    storage=Storage(),
    schemata='Dates',
    widget=bika_DateTimeWidget(
        label=_("Date Sampled")
    ),
)

DateReceived = DateTimeField(
    'DateReceived',
    storage=Storage(),
    schemata='Dates',
    default_method='current_date',
    widget=bika_DateTimeWidget(
        label=_("Date Received")
    ),
)

DateOpened = DateTimeField(
    'DateOpened',
    storage=Storage(),
    schemata='Dates',
    widget=bika_DateTimeWidget(
        label=_("Date Opened")
    ),
)

ExpiryDate = DateTimeField(
    'ExpiryDate',
    storage=Storage(),
    schemata='Dates',
    required=1,
    widget=bika_DateTimeWidget(
        label=_("Expiry Date")
    ),
)

DateExpired = DateTimeField(
    'DateExpired',
    storage=Storage(),
    schemata='Dates',
    widget=bika_DateTimeWidget(
        label=_("Date Expired"),
        visible={'edit': 'hidden'}
    ),
)

DateDisposed = DateTimeField(
    'DateDisposed',
    storage=Storage(),
    schemata='Dates',
    widget=bika_DateTimeWidget(
        label=_("Date Disposed"),
        visible={'edit': 'hidden'}
    ),
)

ReferenceResults = ReferenceResultsField(
    'ReferenceResults',
    storage=Storage(),
    schemata='Reference Values',
    required=1,
    subfield_validators={
        'result': 'referencevalues_validator',
        'min': 'referencevalues_validator',
        'max': 'referencevalues_validator',
        'error': 'referencevalues_validator'},
    widget=ReferenceResultsWidget(
        label=_("Expected Values")
    ),
)

SupplierUID = ComputedField(
    'SupplierUID',
    expression='context.aq_parent.UID()',
    widget=ComputedWidget(
        visible=False
    ),
)

ReferenceDefinitionUID = ComputedField(
    'ReferenceDefinitionUID',
    expression='context.getReferenceDefinition().UID() '
               'if context.getReferenceDefinition().UID() else None',
    widget=ComputedWidget(
        visible=False
    ),
)

schema = BikaSchema.copy() + Schema((
    ReferenceDefinition,
    Blank,
    Hazardous,
    Manufacturer,
    CatalogueNumber,
    LotNumber,
    Remarks,
    DateSampled,
    DateReceived,
    DateOpened,
    ExpiryDate,
    DateExpired,
    DateDisposed,
    ReferenceResults,
    SupplierUID,
    ReferenceDefinitionUID
))

schema['title'].schemata = 'Description'
