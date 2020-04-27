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
from bika.lims.interfaces import IBikaCatalogReport
from zope.interface import implements

# Using a variable to avoid plain strings in code
CATALOG_REPORT_LISTING = "bika_catalog_report"

# Defining the indexes for this catalog
_indexes_dict = {
    "getClientUID": "FieldIndex",
}

# Defining the columns for this catalog
_columns_list = [
    "getClientURL",
    "getFileSize",
    "getCreatorFullName",
    "getClientTitle"
]

# Adding basic indexes
_base_indexes_copy = BASE_CATALOG_INDEXES.copy()
_indexes_dict.update(_base_indexes_copy)
# Adding basic columns
_base_columns_copy = BASE_CATALOG_COLUMNS[:]
_columns_list += _base_columns_copy
# Defining the types for this catalog
_types_list = ["Report", ]

bika_catalog_report_definition = {
    # This catalog contains the metacolumns to list
    # reports in bikalisting
    CATALOG_REPORT_LISTING: {
        "types": _types_list,
        "indexes": _indexes_dict,
        "columns": _columns_list,
    }
}


class BikaCatalogReport(BaseCatalog):
    """
    Catalog to list reports in BikaListing
    """
    implements(IBikaCatalogReport)

    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_REPORT_LISTING,
                             "Catalog Report Listing",
                             "BikaCatalogReportListing")


InitializeClass(BikaCatalogReport)
