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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import re

import six
from bika.lims import APIError
from bika.lims.api import fail
from magnitude import Magnitude
from magnitude import MagnitudeError
from magnitude import mg
from magnitude import new_mag

_marker = object()


def is_magnitude(value):
    """Returns whether the value is a magnitude object

    :param value: the object to check
    :return: True if value is a magnitude object
    :rtype: bool
    """
    return isinstance(value, Magnitude)


def get_magnitude(value, default=_marker):
    """Returns the Magnitude object that represents the value

    :param value: a string that representing a number and unit (e.g. 10 mL)
    :param default: default value to convert to a magnitude object
    :type value: str or Magnitude
    :return: Magnitude object
    :rtype: magnitude.Magnitude
    """
    if is_magnitude(value):
        # A Magnitude object already
        return value

    if not value or not isinstance(value, six.string_types):
        # Handle empty and non-str values properly
        if default is _marker:
            fail("{} is not supported.".format(repr(value)))
        return get_magnitude(default)

    # Split number and unit(s)
    matches = re.match(r"([.\d]+)\s*(\w+.*)", value)
    groups = matches and matches.groups() or []
    if len(groups) != 2:
        if default is _marker:
            fail("No valid format: {}".format(value))
        return get_magnitude(default)

    # L (litter) unit is commonly used to avoid confusion with the number 1,
    # but is not supported by magnitude
    # Create the magnitude for SI derived unit L (=litter)
    # https://github.com/juanre/magnitude/blob/master/magnitude.py#L1147
    new_mag("L", Magnitude(0.001, m=3))

    # Get the magnitude
    try:
        return mg(float(groups[0]), groups[1])
    except MagnitudeError as e:
        if default is _marker:
            fail(e.message)
        return get_magnitude(default)


def get_quantity(value, unit=None, num_digits=16):
    """Returns the quantity of the value that represents a number and unit

    :param value: the value to extract the quantity from
    :param unit: the basic or derived SI unit to convert to
    :param num_digits: the number of digits to consider for rounding
    :type value: str or Magnitude
    :type unit: str
    :return: the quantity of the value in the given units
    :rtype: float
    """
    mag = get_magnitude(value)
    if unit:
        mag.ounit(unit)
    return round(mag.toval(), num_digits)


def is_volume(value):
    """Returns whether the value passed in represents a valid volume

    :param value: the value to check
    :type value: str or Magnitude
    :return: True if the value passed in represents a volume
    :rtype: bool
    """
    try:
        # Get the magnitude and check if can be converted to "l" (volume unit)
        get_quantity(value, "l")
        return True
    except (MagnitudeError, APIError):
        return False


def is_weight(value):
    """Returns whether the value passed in represents a valid weight

    :param value: the value to check
    :type value: str or Magnitude
    :return: True if the value passed in represents a weight
    :rtype: bool
    """
    try:
        # Get the magnitude and check if can be converted to "g" (weight unit)
        get_quantity(value, "g")
        return True
    except (MagnitudeError, APIError):
        return False
