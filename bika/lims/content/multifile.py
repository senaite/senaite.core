# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes import atapi
from Products.Archetypes.public import BaseContent
from bika.lims import config
from bika.lims.content.schema.multifile import schema
from bika.lims.interfaces import IMultifile
from zope.interface import implements


class Multifile(BaseContent):
    # It implements the IEthnicity interface
    implements(IMultifile)
    schema = schema


# Activating the content type in Archetypes' internal types registry
atapi.registerType(Multifile, config.PROJECTNAME)
