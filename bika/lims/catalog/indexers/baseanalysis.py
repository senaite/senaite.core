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

from Products.CMFPlone.CatalogTool import sortable_title as _sortable_title
from bika.lims.interfaces import IBaseAnalysis
from plone.indexer import indexer


@indexer(IBaseAnalysis)
def sortable_title(instance):
    sort_key = instance.getSortKey()
    if sort_key is None:
        sort_key = 999999
    title = _sortable_title(instance)
    if callable(title):
        title = title()
    return "{:010.3f}{}".format(sort_key, title)
