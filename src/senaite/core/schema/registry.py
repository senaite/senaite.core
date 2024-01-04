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

from senaite.core.schema.fields import DataGridField as BaseDataGridField
from senaite.core.schema.fields import DataGridRow as BaseDataGridRow

try:
    from plone.registry.field import PersistentField
except ImportError:
    class PersistentField(object):
        pass


class DataGridField(PersistentField, BaseDataGridField):
    """Use this field for registry entries

    https://pypi.org/project/plone.registry/#persistent-fields
    https://community.plone.org/t/there-is-no-persistent-field-equivalent-for-the-field-a-of-type-b
    """
    pass


class DataGridRow(PersistentField, BaseDataGridRow):
    """Use this field for registry entries

    https://pypi.org/project/plone.registry/#persistent-fields
    https://community.plone.org/t/there-is-no-persistent-field-equivalent-for-the-field-a-of-type-b
    """
    pass
