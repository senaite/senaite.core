# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes import atapi
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

# 'Key' field is name of the Cache object, must be Unique
Key = atapi.StringField(
    'Key',
    storage=Storage(),
    default='',
)

# 'Value' is ID of the last created object. Must be increased before using.
Value = atapi.StringField(
    'Value',
    storage=Storage(),
    default='',
)

schema = BikaSchema.copy() + atapi.Schema((
    Key,
    Value
))

schema['title'].widget.visible = False
