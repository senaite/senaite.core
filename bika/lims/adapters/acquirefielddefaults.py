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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFPlone.interfaces import IPloneSiteRoot
from bika.lims.interfaces import IAcquireFieldDefaults
from zope.interface import implements

_marker = []


class AcquireFieldDefaults(object):
    """Default behaviour for bika.lims.interfaces.IAcquireFieldDefaults.

    Simply works the way up the acquisition, looking for the specified (or
    identically named) field, and returns the found value.

    If no value is found, the original AT default is used.  In this case we
    return None, which is ignored by our handler in monkey/Field.py

    """
    implements(IAcquireFieldDefaults)

    def __init__(self, context):
        self.context = context
        self.sort = 1000

    def __call__(self, field):

        acquire = getattr(field, 'acquire', True)
        if acquire:
            fieldname = getattr(field, 'acquire_fieldname', field.getName())
            current = self.context
            while hasattr(current, 'aq_parent'):
                current = current.aq_parent
                if IPloneSiteRoot.providedBy(current):
                    break
                if fieldname in current.Schema()._names:
                    value = current.Schema()[fieldname].get(current)
                    if value is not None:
                        return value
