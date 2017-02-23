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
    # Results File that system wanted to import
    atapi.StringField('ImportedFile', default=''),

    atapi.StringField('Instrument', default=''),

    atapi.StringField('Interface', default=''),

    atapi.StringField('Results', default=''),
))

schema['title'].widget.visible = False


class AutoImportLog(BaseContent):
    """
    This object will have some information/log about auto-import process
    once they are done(failed).
    """
    schema = schema


# Activating the content type in Archetypes' internal types registry
atapi.registerType(AutoImportLog, config.PROJECTNAME)
