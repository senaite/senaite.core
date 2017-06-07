# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims.content.schema.bikaschema import BikaSchema

schema = BikaSchema.copy()

schema['description'].widget.visible = True
schema['description'].schemata = 'default'
