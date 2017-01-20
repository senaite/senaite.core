# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from zope.interface import implements
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims import bikaMessageFactory as _
from bika.lims import config


schema = BikaSchema.copy() + atapi.Schema((

    atapi.StringField('Key',default=''),
    atapi.StringField('Value',default='')

))

class BikaCache(BaseContent):
    schema = schema

# Activating the content type in Archetypes' internal types registry
atapi.registerType(BikaCache, config.PROJECTNAME)
