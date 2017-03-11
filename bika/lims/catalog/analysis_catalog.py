# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.interfaces import IBikaAnalysisCatalog


# Using a variable to avoid plain strings in code
CATALOG_ANALYSIS_LISTING = 'bika_analysis_catalog'

bika_catalog_analysis_listing_definition = {
    # This catalog contains the metacolumns to list
    # analyses in bikalisting
    CATALOG_ANALYSIS_LISTING: {
        'types':   ['Analysis', 'ReferenceAnalysis', 'DuplicateAnalysis', ],
        # If it is a an Analysis, its parent will be a Analysis Request
        # If it is a an Reference Analysis its parent is a Reference Sample
        'indexes': {
            # Minimum indexes for bika_listing
            # TODO: Can be removed?
            'id': 'FieldIndex',
            'getId': 'FieldIndex',
            # Necessary to avoid reindexing whole catalog when we need to
            # reindex only one object. ExtendedPathIndex also could be used.
            'path': 'PathIndex',
            'created': 'DateIndex',
            'Creator': 'FieldIndex',
            # TODO: Can be removed? Same as id
            'sortable_title': 'FieldIndex',
            'review_state': 'FieldIndex',
            'worksheetanalysis_review_state': 'FieldIndex',
            'cancellation_state': 'FieldIndex',
            'portal_type': 'FieldIndex',
            'UID': 'FieldIndex',
            'allowedRolesAndUsers': 'KeywordIndex',
            'getParentUID': 'FieldIndex',
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
        },
        'columns': [
            'UID',
            'getId',
            'Title',
            'created',
            'Creator',
            'portal_type',
            # TODO-catalog: review_state and getObjectWorkflowStates contains
            # the same state
            'review_state',
            'worksheetanalysis_review_state',
            'getObjectWorkflowStates',
            'getRequestID',
            'getReferenceAnalysesGroupID',
            'getResultCaptureDate',
            'getPriority',
            'getParentURL',
            'getAnalysisRequestURL',
            'getParentTitle',
            'getClientTitle',
            'getClientURL',
            'getAnalysisRequestTitle',
            'getAllowedMethodsAsTuples',
            'getResult',
            'getCalculation',
            'getUnit',
            'getKeyword',
            'getCategoryTitle',
            'getInterimFields',
            'getSamplePartitionID',
            'getRemarks',
            'getRetested',
            'getExpiryDate',
            'getDueDate',
            'getReferenceResults',
            # Used in duplicated analysis objects
            'getAnalysisPortalType',
            'isInstrumentValid',
            'getCanMethodBeChanged',
            # Columns from method
            'getMethodUID',
            'getMethodTitle',
            'getMethodURL',
            'getInstrumentUID',
            'getAnalyst',
            'getAnalystName',
            'hasAttachment',
            'getNumberOfRequiredVerifications',
            'isSelfVerificationEnabled',
            'getSubmittedBy',
            'getVerificators',
            'getLastVerificator',
            'getIsReflexAnalysis',
            # TODO-performance: All that comes from services could be
            # defined as a service metacolumn instead of an analysis one
            'getServiceTitle',
            'getResultOptionsFromService',
            'getServiceUID',
            'getDepartmentUID',
            'getInstrumentEntryOfResults',
            'getServiceDefaultInstrumentUID',
            'getServiceDefaultInstrumentTitle',
            'getServiceDefaultInstrumentURL',
            'getResultsRangeNoSpecs',
            'getSampleTypeUID',
            'getClientOrderNumber',
            'getDateReceived',
        ]
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
