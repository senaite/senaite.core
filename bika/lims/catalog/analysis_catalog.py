# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from zope.interface import implements
from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.interfaces import IBikaAnalysisCatalog
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS

# To prevent unnecessary complexity, the accessor methods are duplicated in
# each of the analysis content-types.  When adding or removing indexes and
# columns in this catalog, you will need to verify/add/remove accessors
# or schema fields for all affected types in content/*analysis.py.

# Using a variable to avoid plain strings in code
CATALOG_ANALYSIS_LISTING = 'bika_analysis_catalog'
# Defining the indexes for this catalog
_indexes_dict = {
    'worksheetanalysis_review_state': 'FieldIndex',
    'cancellation_state': 'FieldIndex',
    'getParentUID': 'FieldIndex',
    'getSampleID': 'FieldIndex',
    'getAnalysisRequestUID': 'FieldIndex',
    'getDepartmentUID': 'FieldIndex',
    'getDueDate': 'DateIndex',
    'getDateSampled': 'DateIndex',
    'getDateReceived': 'DateIndex',
    'getResultCaptureDate': 'DateIndex',
    'getDateAnalysisPublished': 'DateIndex',
    'getClientUID': 'FieldIndex',
    'getAnalyst': 'FieldIndex',
    'getRequestID': 'FieldIndex',
    'getClientOrderNumber': 'FieldIndex',
    'getKeyword': 'FieldIndex',
    'getServiceUID': 'FieldIndex',
    'getCategoryUID': 'FieldIndex',
    'getPointOfCapture': 'FieldIndex',
    'getSamplePartitionUID': 'FieldIndex',
    'getSampleUID': 'FieldIndex',
    'getSampleTypeUID': 'FieldIndex',
    'getSamplePointUID': 'FieldIndex',
    'getRetested': 'FieldIndex',
    'getReferenceAnalysesGroupID': 'FieldIndex',
    'getMethodUID': 'FieldIndex',
    'getInstrumentUID': 'FieldIndex',
    'getBatchUID': 'FieldIndex',
    'getSampleConditionUID': 'FieldIndex',
    'getAnalysisRequestPrintStatus': 'FieldIndex',
    'getWorksheetUID': 'FieldIndex',
    'getOriginalReflexedAnalysisUID': 'FieldIndex',
}
# Defining the columns for this catalog
_columns_list = [
    'worksheetanalysis_review_state',
    'getAttachmentUIDs',
    'getRequestID',
    'getReferenceAnalysesGroupID',
    'getResultCaptureDate',
    'getParentURL',
    'getAnalysisRequestURL',
    'getParentTitle',
    'getParentUID',
    'getClientTitle',
    'getClientURL',
    'getAnalysisRequestTitle',
    'getResult',
    'getFormattedResult',
    'getCalculation',
    'getUnit',
    'getKeyword',
    'getCategoryTitle',
    'getInterimFields',
    'getSamplePartitionID',
    'getRemarks',
    'getRetested',
    'getExpiryDate',
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
    # TODO-performance: All that comes from services could be
    # defined as a service metacolumn instead of an analysis one
    'getResultOptions',
    'getServiceUID',
    'getDepartmentUID',
    'getInstrumentEntryOfResults',
    'getAllowedInstrumentUIDs',
    'getInstrumentUID',
    'getResultsRange',
    'getSampleTypeUID',
    'getClientOrderNumber',
    'getDateReceived',
    'getClientReference',
    'getSampleID',
    'getSampleTypeID',
    'getClientReference',

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
