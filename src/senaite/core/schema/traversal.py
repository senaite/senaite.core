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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from plone.dexterity.utils import resolveDottedName
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError


@adapter(Interface, IBrowserRequest)
@implementer(ITraversable)
class FieldTraversal(object):
    """Allow to traverse schema fields via the ++field++ namespace.
    """
    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        if "." in name:
            # we expect the dotted schema interface + the fieldname
            iface, fieldname = name.rsplit(".", 1)
            schema = resolveDottedName(iface)
            field = schema.get(fieldname)
        else:
            fields = api.get_fields(self.context)
            field = fields.get(name)
        if not field:
            raise TraversalError(name)
        field = field.bind(self.context)
        return field
