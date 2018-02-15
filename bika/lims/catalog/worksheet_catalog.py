# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import implements
from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS
# Bika LIMS imports
from bika.lims.interfaces import IBikaCatalogWorksheetListing


# Using a variable to avoid plain strings in code
CATALOG_WORKSHEET_LISTING = 'bika_catalog_worksheet_listing'
# Defining the types for this catalog
_types_list = ['Worksheet', ]
# Defining the indexes for this catalog
_indexes_dict = {
    'getAnalyst': 'FieldIndex',
    'getWorksheetTemplateTitle': 'FieldIndex',
    'getAnalysesUIDs': 'KeywordIndex',
}
# Defining the columns for this catalog
_columns_list = [
    'getAnalyst',
    'getDepartmentUIDs',
    'getWorksheetTemplateUID',
    'getWorksheetTemplateTitle',
    'getWorksheetTemplateURL',
    'getAnalysesUIDs',
    # TODO-catalog: getLayout returns a dictionary, too big?
    'getLayout',
    # Only used to list
    'getNumberOfQCAnalyses',
    'getNumberOfRegularAnalyses',
    'getNumberOfRegularSamples',
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
        'types':   _types_list,
        'indexes': _indexes_dict,
        'columns': _columns_list
    }
}


class BikaCatalogWorksheetListing(BikaCatalogTool):
    """
    Catalog for Auto import listings
    """
    implements(IBikaCatalogWorksheetListing)

    def __init__(self):
        BikaCatalogTool.__init__(self, CATALOG_WORKSHEET_LISTING,
                                 'Bika Catalog Worksheet Listing',
                                 'BikaCatalogWorksheetListing')


InitializeClass(BikaCatalogWorksheetListing)
