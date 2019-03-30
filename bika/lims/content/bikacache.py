# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from zope.interface import implements
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims import bikaMessageFactory as _
from bika.lims import config


schema = BikaSchema.copy() + atapi.Schema((
    #'Key' field is name of the Cache object, must be Unique
    atapi.StringField('Key',default=''),

    # 'Value' is ID of the last created object. Must be inscreased before using.
    atapi.StringField('Value',default='')

))

schema['title'].widget.visible = False

class BikaCache(BaseContent):
    """
    BikaCache objects stores information about 'Last Created ID's of different
    types. For each object type, there must be only one Cache object, and the ID
    of its Last Created Object.
    It is used to avoid querying whole catalog just to get the highest ID for any
    kind of object.
    """
    schema = schema

# Activating the content type in Archetypes' internal types registry
atapi.registerType(BikaCache, config.PROJECTNAME)
