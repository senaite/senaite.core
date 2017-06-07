# -*- coding: utf-8 -*-

from bika.lims.content.schema.bikaschema import BikaSchema

schema = BikaSchema.copy()

schema['description'].schemata = 'default'
schema['description'].widget.visible = True
