# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import BooleanField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import ReferenceResultsField
from bika.lims.browser.widgets import ReferenceResultsWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

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
        label=_("Reference Values"),
        description=_(
            "Click on Analysis Categories (against shaded backgroundto see "
            "Analysis Services in each category. Enter minimum and maximum "
            "values to indicate a valid results range. Any result outside "
            "this range will raise an alert. The % Error field allows for an "
            "% uncertainty to be considered when evaluating results against "
            "minimum and maximum values. A result out of range but still in "
            "range if the % error is taken into consideration, will raise a "
            "less severe alert.")
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

schema = BikaSchema.copy() + Schema((
    ReferenceResults,
    Blank,
    Hazardous
))

schema['title'].schemata = 'Description'
schema['title'].widget.visible = True
schema['description'].schemata = 'Description'
schema['description'].widget.visible = True
