# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import BooleanField, ComputedField, \
    ReferenceField, StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, ComputedWidget, \
    StringWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
from bika.lims.browser.widgets.referencewidget import ReferenceWidget, \
    ReferenceWidget as brw
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

RetentionPeriod = DurationField(
    'RetentionPeriod',
    storage=Storage(),
    required=1,
    default_method='getDefaultLifetime',
    widget=DurationWidget(
        label=_("Retention Period"),
        description=_(
            "The period for which un-preserved samples of this type "
            "can be kept before "
            "they expire and cannot be analysed any further")
    )
)

Hazardous = BooleanField(
    'Hazardous',
    storage=Storage(),
    default=False,
    widget=BooleanWidget(
        label=_("Hazardous"),
        description=_(
            "Samples of this type should be treated as hazardous")
    )
)

SampleMatrix = ReferenceField(
    'SampleMatrix',
    storage=Storage(),
    required=0,
    allowed_types=('SampleMatrix',),
    vocabulary='SampleMatricesVocabulary',
    relationship='SampleTypeSampleMatrix',
    referenceClass=HoldingReference,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Sample Matrix")
    )
)

Prefix = StringField(
    'Prefix',
    storage=Storage(),
    required=True,
    widget=StringWidget(
        label=_("Sample Type Prefix")
    )
)

MinimumVolume = StringField(
    'MinimumVolume',
    storage=Storage(),
    required=1,
    widget=StringWidget(
        label=_("Minimum Volume"),
        description=_(
            "The minimum sample volume required for analysis eg. '10 "
            "ml' or '1 kg'.")
    )
)

ContainerType = ReferenceField(
    'ContainerType',
    storage=Storage(),
    required=0,
    allowed_types=('ContainerType',),
    vocabulary='ContainerTypesVocabulary',
    relationship='SampleTypeContainerType',
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Default Container Type"),
        description=_(
            "The default container type. New sample partitions "
            "are automatically assigned a container of this "
            "type, unless it has been specified in more details "
            "per analysis service")
    )
)

SamplePoints = ReferenceField(
    'SamplePoints',
    storage=Storage(),
    required=0,
    multiValued=1,
    allowed_types=('SamplePoint',),
    vocabulary='SamplePointsVocabulary',
    relationship='SampleTypeSamplePoint',
    widget=brw(
        label=_("Sample Points"),
        description=_(
            "The list of sample points from which this sample "
            "type can be collected.  If no sample points are "
            "selected, then all sample points are available.")
    )
)

SamplePointTitle = ComputedField(
    'SamplePointTitle',
    storage=Storage(),
    expression="[o.Title() for o in context.getSamplePoints()]",
    widget=ComputedWidget(
        visibile=False,
    )
)

schema = BikaSchema.copy() + Schema((
    RetentionPeriod,
    Hazardous,
    SampleMatrix,
    Prefix,
    MinimumVolume,
    ContainerType,
    SamplePoints,
    SamplePointTitle
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True
