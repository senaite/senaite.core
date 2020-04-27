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
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
# Bika LIMS imports
from bika.lims.interfaces import IBikaCatalogWorksheetListing
from zope.interface import implements

# Using a variable to avoid plain strings in code
CATALOG_WORKSHEET_LISTING = "bika_catalog_worksheet_listing"

# Defining the types for this catalog
_types_list = ["Worksheet", ]
# Defining the indexes for this catalog
_indexes_dict = {
    "getAnalyst": "FieldIndex",
    "getWorksheetTemplateTitle": "FieldIndex",
    "getAnalysesUIDs": "KeywordIndex",
}
# Defining the columns for this catalog
_columns_list = [
    "getAnalyst",
    "getWorksheetTemplateUID",
    "getWorksheetTemplateTitle",
    "getWorksheetTemplateURL",
    "getAnalysesUIDs",
    # Only used to list
    "getNumberOfQCAnalyses",
    "getNumberOfRegularAnalyses",
    "getNumberOfRegularSamples",
    "getProgressPercentage",
]
# Adding basic indexes
_base_indexes_copy = BASE_CATALOG_INDEXES.copy()
_indexes_dict.update(_base_indexes_copy)
# Adding basic columns
_base_columns_copy = BASE_CATALOG_COLUMNS[:]
_columns_list += _base_columns_copy

# Defining the catalog
bika_catalog_worksheet_listing_definition = {
    CATALOG_WORKSHEET_LISTING: {
        "types":   _types_list,
        "indexes": _indexes_dict,
        "columns": _columns_list
    }
}


class BikaCatalogWorksheetListing(BaseCatalog):
    """Catalog for Auto import listings
    """
    implements(IBikaCatalogWorksheetListing)

    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_WORKSHEET_LISTING,
                             "Catalog Worksheet Listing",
                             "BikaCatalogWorksheetListing")


InitializeClass(BikaCatalogWorksheetListing)
