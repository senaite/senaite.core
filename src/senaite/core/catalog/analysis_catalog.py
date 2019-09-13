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

from zope.interface import implements
from App.class_init import InitializeClass
from senaite.core.catalog.bika_catalog_tool import BikaCatalogTool
from senaite.core.interfaces import IBikaAnalysisCatalog
from senaite.core.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
from senaite.core.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS

# To prevent unnecessary complexity, the accessor methods are duplicated in
# each of the analysis content-types.  When adding or removing indexes and
# columns in this catalog, you will need to verify/add/remove accessors
# or schema fields for all affected types in content/*analysis.py.

# Using a variable to avoid plain strings in code
CATALOG_ANALYSIS_LISTING = 'bika_analysis_catalog'
# Defining the indexes for this catalog
_indexes_dict = {
    'sortable_title': 'FieldIndex',
    'getParentUID': 'FieldIndex',
    'getRequestUID': 'FieldIndex',
    'getDueDate': 'DateIndex',
    'getDateSampled': 'DateIndex',
    'getDateReceived': 'DateIndex',
    'getResultCaptureDate': 'DateIndex',
    'getClientUID': 'FieldIndex',
    'getClientTitle': 'FieldIndex',
    'getAnalyst': 'FieldIndex',
    'getRequestID': 'FieldIndex',
    'getClientOrderNumber': 'FieldIndex',
    'getKeyword': 'FieldIndex',
    'getServiceUID': 'FieldIndex',
    'getCategoryUID': 'FieldIndex',
    'getPointOfCapture': 'FieldIndex',
    'getSampleTypeUID': 'FieldIndex',
    # TODO Index 'getSamplePointUID' is only used in reports/selection_macros
    'getSamplePointUID': 'FieldIndex',
    'getReferenceAnalysesGroupID': 'FieldIndex',
    'getMethodUID': 'FieldIndex',
    'getInstrumentUID': 'FieldIndex',
    'getBatchUID': 'FieldIndex',
    'getAnalysisRequestPrintStatus': 'FieldIndex',
    'getWorksheetUID': 'FieldIndex',
    'getOriginalReflexedAnalysisUID': 'FieldIndex',
    'getPrioritySortkey': 'FieldIndex',
    'getAncestorsUIDs': 'KeywordIndex',
    'isSampleReceived': 'BooleanIndex',
    'isRetest': 'BooleanIndex',
}
# Defining the columns for this catalog
_columns_list = [
    'getAttachmentUIDs',
    'getRequestID',
    'getReferenceAnalysesGroupID',
    'getResultCaptureDate',
    'getParentURL',
    'getRequestURL',
    'getParentTitle',
    'getParentUID',
    'getClientTitle',
    'getClientURL',
    'getRequestTitle',
    'getResult',
    'getCalculationUID',
    'getUnit',
    'getKeyword',
    'getCategoryTitle',
    'getInterimFields',
    'getRemarks',
    'getRetestOfUID',
    'getDateSampled',
    'getDueDate',
    'getReferenceResults',
    # Used in duplicated analysis objects
    'getAnalysisPortalType',
    'isInstrumentValid',
    # Columns from method
    'getMethodUID',
    'getMethodTitle',
    'getMethodURL',
    'getAllowedMethodUIDs',
    'getAnalyst',
    'getAnalystName',
    'getNumberOfRequiredVerifications',
    'getNumberOfVerifications',
    'isSelfVerificationEnabled',
    'getSubmittedBy',
    'getVerificators',
    'getLastVerificator',
    'getIsReflexAnalysis',
    'getPrioritySortkey',
    # TODO-performance: All that comes from services could be
    # defined as a service metacolumn instead of an analysis one
    'getResultOptions',
    'getServiceUID',
    'getInstrumentEntryOfResults',
    'getAllowedInstrumentUIDs',
    'getInstrumentUID',
    'getResultsRange',
    'getSampleTypeUID',
    'getClientOrderNumber',
    'getDateReceived',
]
# Adding basic indexes
_base_indexes_copy = BASE_CATALOG_INDEXES.copy()
_indexes_dict.update(_base_indexes_copy)
# Adding basic columns
_base_columns_copy = BASE_CATALOG_COLUMNS[:]
_columns_list += _base_columns_copy

# Defining the types for this catalog
_types_list = ['Analysis', 'ReferenceAnalysis', 'DuplicateAnalysis', ]

bika_catalog_analysis_listing_definition = {
    CATALOG_ANALYSIS_LISTING: {
        'types': _types_list,
        'indexes': _indexes_dict,
        'columns': _columns_list,
    }
}


class BikaAnalysisCatalog(BikaCatalogTool):
    """
    Catalog for Analysis content types
    """
    implements(IBikaAnalysisCatalog)

    def __init__(self):
        BikaCatalogTool.__init__(self, CATALOG_ANALYSIS_LISTING,
                                 'Bika Analysis Catalog',
                                 'BikaAnalysisCatalog')


InitializeClass(BikaAnalysisCatalog)


"""
"""
