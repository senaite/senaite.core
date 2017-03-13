# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from zope.interface import implements
from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
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


class BikaCatalogAnalysisRequestListing(BikaCatalogTool):
    """
    Catalog to list analysis requests in BikaListing
    """
    implements(IBikaCatalogAnalysisRequestListing)

    def __init__(self):
        BikaCatalogTool.__init__(self, CATALOG_ANALYSIS_REQUEST_LISTING,
                                 'Bika Catalog Analysis Request Listing',
                                 'BikaCatalogAnalysisRequestListing')

InitializeClass(BikaCatalogAnalysisRequestListing)
