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

from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName


def getValues(self, prop_name):
    ptool = getToolByName(self, "portal_properties", None)
    if ptool and hasattr(ptool, "extensions_properties"):
        return ptool.extensions_properties.getProperty(prop_name, None)
    else:
        return None


def makeDisplayList(values=None, add_select=True):
    if values and type(values) not in [type([]), type(())]:
        values = (values,)
    if not values:
        values = []
    if add_select:
        results = [["", "Select"], ]
    else:
        results = []
    for x in values:
        results.append([x, x])
    values_tuple = tuple(results)
    return DisplayList(values_tuple)


def getDisplayList(self, prop_name=None, add_select=True):
    return makeDisplayList(getValues(self, prop_name), add_select)
