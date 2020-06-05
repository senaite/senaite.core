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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.GenericSetup.interfaces import INode
from zope.interface import Interface


class IFieldNode(INode):
    """Import/Export fields
    """

    def get_field_value():
        """Get the field value with the accessor
        """

    def set_field_value():
        """Set the field value with the mutator
        """

    def get_json_value():
        """Get the JSON converted field value
        """

    def parse_json_value(value):
        """Parse the JSON value
        """

    def set_node_value(node):
        """Set the value of the node to the field
        """

    def get_node_value(value):
        """Get a node from the value
        """


class IRecordField(Interface):
    """Marker interface for Record Fields

    N.B. There is no official interface provided by this Field!
    """
