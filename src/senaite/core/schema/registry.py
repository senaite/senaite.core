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

from senaite.core.schema.fields import DataGridField as BaseDataGridField
from senaite.core.schema.fields import DataGridRow as BaseDataGridRow

try:
    from plone.registry.field import PersistentField
    from plone.registry.interfaces import IPersistentField
except ImportError:
    class PersistentField(object):
        pass

    class IPersistentField(object):
        pass


def _clone_persistent_field(field):
    """Create a fresh clone of a persistent DataGrid field

    When plone.registry registers an interface, it calls
    IPersistentField(field_instance) for constrained properties
    like value_type. If the field already provides IPersistentField
    (as our DataGrid fields do via PersistentField inheritance),
    the interface call protocol returns the same instance.

    This becomes a problem when the same field instance is stored
    in the ZODB across multiple connections (e.g. test layer
    setup/teardown cycles): the module-level field instance retains
    a _p_jar reference to the now-closed ZODB connection, causing
    ConnectionStateError.

    By implementing __conform__, we intercept the interface call
    and always return a fresh clone with no ZODB connection.
    """
    clone = field.__class__.__new__(field.__class__)
    clone.__dict__.update(field.__dict__)
    return clone


class DataGridField(PersistentField, BaseDataGridField):
    """Use this field for registry entries

    https://pypi.org/project/plone.registry/#persistent-fields
    """

    def __conform__(self, iface):
        if iface is IPersistentField:
            return _clone_persistent_field(self)
        return None


class DataGridRow(PersistentField, BaseDataGridRow):
    """Use this field for registry entries

    https://pypi.org/project/plone.registry/#persistent-fields
    """

    def __conform__(self, iface):
        if iface is IPersistentField:
            return _clone_persistent_field(self)
        return None
