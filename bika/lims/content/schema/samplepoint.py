# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from sys import maxint

from Products.Archetypes.Field import BooleanField, ComputedField, \
    ReferenceField, StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, ComputedWidget, \
    FileWidget, StringWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import CoordinateField
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import CoordinateWidget
from bika.lims.browser.widgets import DurationWidget
from bika.lims.browser.widgets.referencewidget import ReferenceWidget as brw
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema
from plone.app.blob.field import FileField as BlobFileField

Latitude = CoordinateField(
    'Latitude',
    storage=Storage(),
    schemata='Location',
    widget=CoordinateWidget(
        label=_("Latitude"),
        description=_(
            "Enter the Sample Point's latitude in degrees 0-90, minutes 0-59, "
            "seconds 0-59 and N/S indicator")
    ),
)

Longitude = CoordinateField(
    'Longitude',
    storage=Storage(),
    schemata='Location',
    widget=CoordinateWidget(
        label=_("Longitude"),
        description=_(
            "Enter the Sample Point's longitude in degrees 0-180, minutes "
            "0-59, seconds 0-59 and E/W indicator")
    ),
)

Elevation = StringField(
    'Elevation',
    storage=Storage(),
    schemata='Location',
    widget=StringWidget(
        label=_("Elevation"),
        description=_("The height or depth at which the sample has to be taken")
    ),
)

SamplingFrequency = DurationField(
    'SamplingFrequency',
    storage=Storage(),
    vocabulary_display_path_bound=maxint,
    widget=DurationWidget(
        label=_("Sampling Frequency"),
        description=_(
            "If a sample is taken periodically at this sample point, "
            "enter frequency here, e.g. weekly")
    ),
)

SampleTypes = ReferenceField(
    'SampleTypes',
    storage=Storage(),
    required=0,
    multiValued=1,
    allowed_types=('SampleType',),
    vocabulary='SampleTypesVocabulary',
    relationship='SamplePointSampleType',
    widget=brw(
        label=_("Sample Types"),
        description=_("The list of sample types that can be collected "
                      "at this sample point.  If no sample types are "
                      "selected, then all sample types are available.")
    ),
)

SampleTypeTitle = ComputedField(
    'SampleTypeTitle',
    storage=Storage(),
    expression="[o.Title() for o in context.getSampleTypes()]",
    widget=ComputedWidget(
        visible=False,
    ),
)

Composite = BooleanField(
    'Composite',
    storage=Storage(),
    default=False,
    widget=BooleanWidget(
        label=_("Composite"),
        description=_(
            "Check this box if the samples taken at this point are 'composite' "
            "and put together from more than one sub sample, e.g. several "
            "surface "
            "samples from a dam mixed together to be a representative sample "
            "for the dam. "
            "The default, unchecked, indicates 'grab' samples")
    ),
)

AttachmentFile = BlobFileField(
    'AttachmentFile',
    storage=Storage(),
    widget=FileWidget(
        label=_("Attachment")
    ),
)

schema = BikaSchema.copy() + Schema((
    Latitude,
    Longitude,
    Elevation,
    SamplingFrequency,
    SampleTypes,
    SampleTypeTitle,
    Composite,
    AttachmentFile
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'
