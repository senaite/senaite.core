# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes.Field import LinesField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import PicklistWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.content.schema.bikaschema import BikaSchema
from bika.lims.content.schema import Storage

PortalTypes = LinesField(
    'PortalTypes',
    storage=Storage,
    vocabulary='getPortalTypes',
    widget=PicklistWidget(
        label=_("Portal Types"),
        description=_("Select the types that this ID is used to identify."),
    ),
)

schema = BikaSchema.copy() + Schema((
    PortalTypes,
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'
