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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import api
from plone.dexterity.content import Container as BaseContainer
from plone.dexterity.content import Item as BaseItem
from senaite.core.interfaces import IContainer
from senaite.core.interfaces import IItem
from zope.interface import implementer


@implementer(IContainer)
class Container(BaseContainer):
    """Base class for SENAITE folderish contents
    """
    security = ClassSecurityInfo()

    @security.private
    def accessor(self, fieldname, raw=False):
        """Return the field accessor for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        field = schema[fieldname]
        if raw:
            if hasattr(field, "get_raw"):
                return field.get_raw
            return field.getRaw
        return field.get

    @security.private
    def mutator(self, fieldname):
        """Return the field mutator for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        return schema[fieldname].set


@implementer(IItem)
class Item(BaseItem):
    """Base class for SENAITE contentish contents
    """
    security = ClassSecurityInfo()

    @security.private
    def accessor(self, fieldname, raw=False):
        """Return the field accessor for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        field = schema[fieldname]
        if raw:
            if hasattr(field, "get_raw"):
                return field.get_raw
            return field.getRaw
        return field.get

    @security.private
    def mutator(self, fieldname):
        """Return the field mutator for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        return schema[fieldname].set
