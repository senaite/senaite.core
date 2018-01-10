# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import implements
from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.interfaces import IBikaCatalogAutoImportLogsListing
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS


# Using a variable to avoid plain strings in code
CATALOG_AUTOIMPORTLOGS_LISTING = 'bika_catalog_autoimportlogs_listing'
# Defining the indexes for this catalog
_indexes_dict = {
    'getInstrumentUID': 'FieldIndex',
}
# Defining the columns for this catalog
_columns_list = [
    'getInstrumentUrl',
    'getInstrumentTitle',
    'getImportedFile',
    'getInterface',
    'getResults',
    'getLogTime'
]
# Adding basic indexes
_base_indexes_copy = BASE_CATALOG_INDEXES.copy()
_indexes_dict.update(_base_indexes_copy)
# Adding basic columns
_base_columns_copy = BASE_CATALOG_COLUMNS[:]
_columns_list += _base_columns_copy

# Defining the types for this catalog
_types_list = ['AutoImportLog', ]
bika_catalog_autoimportlogs_listing_definition = {
    CATALOG_AUTOIMPORTLOGS_LISTING: {
        'types': _types_list,
        'indexes': _indexes_dict,
        'columns': _columns_list,
    }
}


class BikaCatalogAutoImportLogsListing(BikaCatalogTool):
    """
    Catalog for Auto import listings
    """
    implements(IBikaCatalogAutoImportLogsListing)

    def __init__(self):
        BikaCatalogTool.__init__(self, CATALOG_AUTOIMPORTLOGS_LISTING,
                                 'Bika Catalog Auto-Import Logs Listing',
                                 'BikaCatalogAutoImportLogsListing')


InitializeClass(BikaCatalogAutoImportLogsListing)
