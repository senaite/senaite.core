# -*- coding: utf-8 -*-

from zope import interface
from z3c.form.interfaces import NO_VALUE


class IDataManager(interface.Interface):
    """Data manager."""

    def get(name):
        """Get the value.

        If no value can be found, raise an error
        """

    def query(name, default=NO_VALUE):
        """Query the name for its value

        If no value can be found, return the default value.
        If read is forbidden, raise an error.
        """

    def set(name, value):
        """Set the value by name

        Returns a list of updated objects
        """

    def can_read():
        """Checks if the object is readable
        """

    def can_write():
        """Checks if the object is writable
        """
