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

from bika.lims import api
from Products.Archetypes.config import UID_CATALOG


def _catalogUID(self, aq, uc=None):
    # skip indexing of temporary objects
    if api.is_temporary(self):
        return
    if not uc:
        uc = api.get_tool(UID_CATALOG)
    url = self._getURL()
    uc.catalog_object(self, url)


def _uncatalogUID(self, aq, uc=None):
    # skip indexing of temporary objects
    if api.is_temporary(self):
        return
    if not uc:
        uc = api.get_tool(UID_CATALOG)
    url = self._getURL()
    # XXX This is an ugly workaround. This method shouldn't be called
    # twice for an object in the first place, so we don't have to check
    # if it is still cataloged.
    rid = uc.getrid(url)
    if rid is not None:
        uc.uncatalog_object(url)
