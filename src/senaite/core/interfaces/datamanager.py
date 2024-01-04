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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

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
