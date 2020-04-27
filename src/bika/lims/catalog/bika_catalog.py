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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.interfaces import IBikaCatalog
from zope.interface import implements

# Using a variable to avoid plain strings in code
BIKA_CATALOG = "bika_catalog"

# Defining the indexes for this catalog
_indexes = {
    "listing_searchable_text": "TextIndexNG3",
}
# Defining the columns for this catalog
_columns = []
# Defining the types for this catalog
_types = []

bika_catalog_definition = {
    BIKA_CATALOG: {
        "types": _types,
        "indexes": _indexes,
        "columns": _columns,
    }
}


class BikaCatalog(BaseCatalog):
    """Bika Catalog
    """
    implements(IBikaCatalog)

    def __init__(self):
        BaseCatalog.__init__(self, "bika_catalog",
                             "Bika Catalog",
                             "BikaCatalog")


InitializeClass(BikaCatalog)
