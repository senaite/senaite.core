# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Schema import Schema
from bika.lims import bikaMessageFactory as _
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema
from bika.lims.fields import ExtStringField, StringWidget

schema = BikaSchema.copy() + Schema((
    ExtStringField(
        'SortKey',
        storage=Storage,
        widget=StringWidget(
            label=_("Sort Key"),
            description=_("Subgroups are sorted with this key in group views")
        )
    ),
))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'
