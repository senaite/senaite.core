# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import sys
import traceback
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
# Bika LIMS imports
from bika.lims import logger
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


class BikaAnalysisCatalog(CatalogTool):

    """Catalog for analysis types"""

    implements(IBikaAnalysisCatalog)

    security = ClassSecurityInfo()
    _properties = ({'id': 'title', 'type': 'string', 'mode': 'w'},)

    title = 'Bika Analysis Catalog'
    id = CATALOG_ANALYSIS_LISTING
    portal_type = meta_type = 'BikaAnalysisCatalog'
    plone_tool = 1

    def __init__(self):
        ZCatalog.__init__(self, self.id)

    security.declareProtected(ManagePortal, 'clearFindAndRebuild')

    def clearFindAndRebuild(self):
        """Empties catalog, then finds all contentish objects (i.e. objects
           with an indexObject method), and reindexes them.
           This may take a long time.
        """
        def indexObject(obj, path):
            self.reindexObject(obj)
        logger.info('Cleaning and rebuilding %s...' % self.id)
        try:
            at = getToolByName(self, 'archetype_tool')
            types = [k for k, v in at.catalog_map.items()
                     if self.id in v]

            self.manage_catalogClear()
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal.ZopeFindAndApply(portal,
                                    obj_metatypes=types,
                                    search_sub=True,
                                    apply_func=indexObject)
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (self.id, e))
        logger.info('%s cleaned and rebuilt' % self.id)


InitializeClass(BikaAnalysisCatalog)
