# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from zope.interface import implements
from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.interfaces import IBikaCatalogSample
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS


# Using a variable to avoid plain strings in code
CATALOG_SAMPLE_LISTING = 'bika_sample_catalog'
# Defining the indexes for this catalog
_indexes_dict = {
}

# Defining the columns for this catalog
_columns_list = [
]

# Adding basic indexes
_base_indexes_copy = BASE_CATALOG_INDEXES.copy()
_indexes_dict.update(_base_indexes_copy)
# Adding basic columns
_base_columns_copy = BASE_CATALOG_COLUMNS[:]
_columns_list += _base_columns_copy
# Defining the types for this catalog
_types_list = ['Sample', ]

bika_catalog_sample_definition = {
    # This catalog contains the metacolumns to list
    # reports in bikalisting
    CATALOG_SAMPLE_LISTING: {
        'types': _types_list,
        'indexes': _indexes_dict,
        'columns': _columns_list,
    }
}


class BikaSampleCatalog(BikaCatalogTool):
    """
    Catalog to list samples in BikaListing
    """
    implements(IBikaCatalogSample)

    def __init__(self):
        BikaCatalogTool.__init__(self, CATALOG_SAMPLE_LISTING,
                                 'Bika Catalog Sample Listing',
                                 'BikaSampleCatalogListing')


InitializeClass(BikaSampleCatalog)