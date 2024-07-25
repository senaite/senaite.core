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

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims.interfaces import IARAnalysesField
from Products.Archetypes.public import Field
from Products.Archetypes.public import ObjectField
from Products.Archetypes.Registry import registerField
from senaite.core.interfaces import IDataManager
from zope.component._api import queryMultiAdapter
from zope.interface import implements

"""Field to manage Analyses on ARs

Please see the assigned doctest at tests/doctests/ARAnalysesField.rst

Run this test from the buildout directory:

    bin/test test_textual_doctests -t ARAnalysesField
"""


class ARAnalysesField(ObjectField):
    """A field that stores Analyses instances
    """
    implements(IARAnalysesField)

    security = ClassSecurityInfo()
    _properties = Field._properties.copy()
    _properties.update({
        "type": "analyses",
        "default": None,
    })

    @security.public
    def get(self, instance, **kw):
        # See `senaite.core.datamanagers.field.sample_analyses`
        dm = queryMultiAdapter(
            (instance, api.get_request(), self), interface=IDataManager)
        return dm.get(**kw)

    @security.private
    def set(self, instance, items, prices=None, specs=None, hidden=None, **kw):
        # See `senaite.core.datamanagers.field.sample_analyses`
        dm = queryMultiAdapter(
            (instance, api.get_request(), self), interface=IDataManager)
        return dm.set(items, prices, specs, hidden, **kw)


registerField(ARAnalysesField,
              title="Analyses",
              description="Manages Analyses of ARs")
