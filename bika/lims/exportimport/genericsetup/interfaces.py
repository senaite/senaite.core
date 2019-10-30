# -*- coding: utf-8 -*-

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
