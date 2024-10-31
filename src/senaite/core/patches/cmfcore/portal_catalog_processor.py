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

PORTAL_CATALOG = "portal_catalog"


def index_in_portal_catalog(obj):
    portal_catalog = api.get_tool(PORTAL_CATALOG)
    catalogs = api.get_catalogs_for(obj)
    if portal_catalog not in catalogs:
        return False
    return True


def index(self, obj, attributes=None):
    if not index_in_portal_catalog(obj):
        return
    catalog = api.get_tool(PORTAL_CATALOG)
    if catalog is not None:
        catalog._indexObject(obj)


def reindex(self, obj, attributes=None, update_metadata=1):
    if not index_in_portal_catalog(obj):
        return
    catalog = api.get_tool(PORTAL_CATALOG)
    if catalog is not None:
        catalog._reindexObject(
            obj,
            idxs=attributes,
            update_metadata=update_metadata)


def unindex(self, obj):
    if not index_in_portal_catalog(obj):
        return
    catalog = api.get_tool(PORTAL_CATALOG)
    if catalog is not None:
        catalog._unindexObject(obj)
