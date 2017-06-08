# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from sys import maxint

from Products.Archetypes.Field import BooleanField, ReferenceField, StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, ReferenceWidget, \
    StringWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

ContainerType = ReferenceField(
    'ContainerType',
    storage=Storage(),
    required=0,
    vocabulary_display_path_bound=maxint,
    allowed_types=('ContainerType',),
    vocabulary='getContainerTypes',
    relationship='ContainerContainerType',
    referenceClass=HoldingReference,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Container Type")
    ),
)

Capacity = StringField(
    'Capacity',
    storage=Storage(),
    required=1,
    default="0 ml",
    widget=StringWidget(
        label=_("Capacity"),
        description=_(
            "Maximum possible size or volume of samples.")
    ),
)

PrePreserved = BooleanField(
    'PrePreserved',
    storage=Storage(),
    validators=('container_prepreservation_validator',),
    default=False,
    widget=BooleanWidget(
        label=_("Pre-preserved"),
        description=_(
            "Check this box if this container is already "
            "preserved."
            "Setting this will short-circuit the preservation "
            "workflow "
            "for sample partitions stored in this container.")
    ),
)

Preservation = ReferenceField(
    'Preservation',
    storage=Storage(),
    required=0,
    vocabulary_display_path_bound=maxint,
    allowed_types=('Preservation',),
    vocabulary='getPreservations',
    relationship='ContainerPreservation',
    referenceClass=HoldingReference,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Preservation"),
        description=_(
            "If this container is pre-preserved, then the "
            "preservation "
            "method could be selected here.")
    ),
)

SecuritySealIntact = BooleanField(
    'SecuritySealIntact',
    storage=Storage(),
    default=True,
    widget=BooleanWidget(
        label=_("Security Seal Intact Y/N")
    ),
)

schema = BikaSchema.copy() + Schema((
    ContainerType,
    Capacity,
    PrePreserved,
    Preservation,
    SecuritySealIntact
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'
