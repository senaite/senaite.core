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

"""Helpers for SENAITE edit-form adapters."""

CHECKED_VALUES = ("true", "1", "selected", "on")


def is_checked(value):
    """Check if a form value represents a checked boolean

    DX boolean checkboxes submit a list of marker values, AT booleans
    a string, JSON callbacks a real bool. Normalize across all three.

    :param value: Value submitted for a boolean field
    :returns: True when the value represents a checked state
    :rtype: bool
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, tuple)):
        return any(is_checked(item) for item in value)
    return str(value).lower() in CHECKED_VALUES
