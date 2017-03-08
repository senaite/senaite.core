# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import sys
import traceback
import transaction
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
# Bika LIMS imports
from bika.lims import logger
from bika.lims.interfaces import IBikaCatalogAnalysisRequestListing


# Using a variable to avoid plain strings in code
CATALOG_ANALYSIS_REQUEST_LISTING = 'bika_catalog_analysisrequest_listing'

bika_catalog_analysisrequest_listing_definition = {
    # This catalog contains the metacolumns to list
    # analysisrequests in bikalisting
    CATALOG_ANALYSIS_REQUEST_LISTING: {
        'types':   ['AnalysisRequest', ],
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
            'cancellation_state': 'FieldIndex',
            # TODO-catalog: can be removed?
            'portal_type': 'FieldIndex',
            'UID': 'FieldIndex',
            'getBatchUID': 'FieldIndex',
            'getClientUID': 'FieldIndex',
            'getSampleUID': 'FieldIndex',
            'getDepartmentUID': 'KeywordIndex',
            'getDateSampled': 'DateIndex',
            'getSamplingDate': 'DateIndex',
            'getSampler': 'FieldIndex',
            'getDateReceived': 'DateIndex',
            'getReceivedBy': 'FieldIndex',
            'getDateVerified': 'DateIndex',
            'getDatePublished': 'DateIndex'
        },
        'columns': [
            'UID',
            'getId',
            'Title',
            'created',
            'Creator',
            'getCreatorFullName',
            'getCreatorEmail',
            'review_state',
            'getObjectWorkflowStates',
            'getPhysicalPath',
            'getSampleUID',
            # Used to print the ID of the Sample in lists
            'getSampleID',
            # Used to create add an anchor to Sample ID that redirects to
            # the Sample view.
            'getSampleURL',
            'getClientOrderNumber',
            'getClientReference',
            'getClientSampleID',
            'getSampler',
            'getSamplerFullName',
            'getSamplerEmail',
            'getBatchUID',
            #  Used to print the ID of the Batch in lists
            'getBatchID',
            'getBatchURL',
            'getClientUID',
            'getClientTitle',
            'getClientURL',
            'getContactUID',
            'getContactUsername',
            'getContactEmail',
            'getContactURL',
            'getContactFullName',
            'getSampleTypeUID',
            'getSampleTypeTitle',
            'getSamplePointUID',
            'getSamplePointTitle',
            'getStorageLocationUID',
            'getStorageLocationTitle',
            'getPriority',
            'getSamplingDate',
            'getDateSampled',
            'getDateReceived',
            'getDateVerified',
            'getDatePublished',
            'getProfilesUID',
            'getProfilesURL',
            'getProfilesTitle',
            'getProfilesTitleStr',
            'getTemplateUID',
            'getTemplateURL',
            'getTemplateTitle',
            'getAnalysesNum',
            'getPrinted',
            'getSamplingDeviationTitle',
            'getLate',
            'getInvoiceExclude',
            'getHazardous',
            'getSamplingWorkflowEnabled',
            'getDepartmentUIDs',

        ]
    }
}


class BikaCatalogAnalysisRequestListing(CatalogTool):
    """
    Catalog to list analysis requests in BikaListing
    """
    implements(IBikaCatalogAnalysisRequestListing)
    title = 'Bika Catalog Analysis Request Listing'
    id = CATALOG_ANALYSIS_REQUEST_LISTING
    portal_type = meta_type = 'BikaCatalogAnalysisRequestListing'
    plone_tool = 1
    security = ClassSecurityInfo()
    _properties = (
      {'id': 'title', 'type': 'string', 'mode': 'w'},)

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
            transaction.commit()
        logger.info('Cleaning and rebuilding %s...' % self.id)
        try:
            at = getToolByName(self, 'archetype_tool')
            types = [k for k, v in at.catalog_map.items()
                     if self.id in v]
            self.manage_catalogClear()
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal.ZopeFindAndApply(
                portal,
                obj_metatypes=types,
                search_sub=True,
                apply_func=indexObject)
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (self.id, e))
        logger.info('%s cleaned and rebuilt' % self.id)


InitializeClass(BikaCatalogAnalysisRequestListing)
