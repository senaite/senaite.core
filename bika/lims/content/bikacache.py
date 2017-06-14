# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.public import BaseContent
from bika.lims import config
from bika.lims.content.schema.bikacache import schema


class BikaCache(BaseContent):
    """BikaCache objects stores information about 'Last Created ID's of 
    different types. For each object type, there must be only one Cache 
    object, and the ID of its Last Created Object. It is used to avoid 
    querying whole catalog just to get the highest ID for any kind of object.
    """
    schema = schema


# Activating the content type in Archetypes' internal types registry
registerType(BikaCache, config.PROJECTNAME)
