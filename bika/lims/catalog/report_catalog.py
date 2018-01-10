# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import implements
from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.interfaces import IBikaCatalogReport
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS


# Using a variable to avoid plain strings in code
CATALOG_REPORT_LISTING = 'bika_catalog_report'
# Defining the indexes for this catalog
_indexes_dict = {'getClientUID': 'FieldIndex',
}

# Defining the columns for this catalog
_columns_list = ['getClientURL',
                 'getFileSize',
                 'getCreatorFullName',
                 'getClientTitle'
]

# Adding basic indexes
_base_indexes_copy = BASE_CATALOG_INDEXES.copy()
_indexes_dict.update(_base_indexes_copy)
# Adding basic columns
_base_columns_copy = BASE_CATALOG_COLUMNS[:]
_columns_list += _base_columns_copy
# Defining the types for this catalog
_types_list = ['Report', ]

bika_catalog_report_definition = {
    # This catalog contains the metacolumns to list
    # reports in bikalisting
    CATALOG_REPORT_LISTING: {
        'types': _types_list,
        'indexes': _indexes_dict,
        'columns': _columns_list,
    }
}


class BikaCatalogReport(BikaCatalogTool):
    """
    Catalog to list reports in BikaListing
    """
    implements(IBikaCatalogReport)

    def __init__(self):
        BikaCatalogTool.__init__(self, CATALOG_REPORT_LISTING,
                                 'Bika Catalog Report Listing',
                                 'BikaCatalogReportListing')


InitializeClass(BikaCatalogReport)
