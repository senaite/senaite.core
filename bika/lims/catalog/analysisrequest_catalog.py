# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import implements
from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.interfaces import IBikaCatalogAnalysisRequestListing
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS


# Using a variable to avoid plain strings in code
CATALOG_ANALYSIS_REQUEST_LISTING = 'bika_catalog_analysisrequest_listing'
# Defining the indexes for this catalog
_indexes_dict = {
    # TODO: Can be removed? Same as id
    'sortable_title': 'FieldIndex',
    'getClientUID': 'FieldIndex',
    'getSampleUID': 'FieldIndex',
    'cancellation_state': 'FieldIndex',
    'getBatchUID': 'FieldIndex',
    'getDateSampled': 'DateIndex',
    'getSamplingDate': 'DateIndex',
    'getDateReceived': 'DateIndex',
    'getDateVerified': 'DateIndex',
    'getDatePublished': 'DateIndex',
    'getSampler': 'FieldIndex',
    'getReceivedBy': 'FieldIndex',
    'getDepartmentUIDs': 'KeywordIndex',
    'getPrinted': 'FieldIndex',
    'getProvince': 'FieldIndex',
    'getDistrict': 'FieldIndex',
    'getClientSampleID': 'FieldIndex',
    'getSampleID': 'FieldIndex',
    # To sort in lists
    'getClientTitle': 'FieldIndex',
    'getPrioritySortkey': 'FieldIndex',
}
# Defining the columns for this catalog
_columns_list = [
    'getCreatorFullName',
    'getCreatorEmail',
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
    'getSamplingDate',
    'getDateSampled',
    'getDateReceived',
    'getDateVerified',
    'getDatePublished',
    'getDistrict',
    'getProfilesUID',
    'getProfilesURL',
    'getProfilesTitle',
    'getProfilesTitleStr',
    'getProvince',
    'getTemplateUID',
    'getTemplateURL',
    'getTemplateTitle',
    'getAnalysesNum',
    'getPrinted',
    'getSamplingDeviationTitle',
    'getPrioritySortkey',
    # TODO: This should be updated through a clock
    'getLate',
    'getInvoiceExclude',
    'getHazardous',
    'getSamplingWorkflowEnabled',
    'getDepartmentUIDs',
]
# Adding basic indexes
_base_indexes_copy = BASE_CATALOG_INDEXES.copy()
_indexes_dict.update(_base_indexes_copy)
# Adding basic columns
_base_columns_copy = BASE_CATALOG_COLUMNS[:]
_columns_list += _base_columns_copy
# Defining the types for this catalog
_types_list = ['AnalysisRequest', ]

bika_catalog_analysisrequest_listing_definition = {
    # This catalog contains the metacolumns to list
    # analysisrequests in bikalisting
    CATALOG_ANALYSIS_REQUEST_LISTING: {
        'types': _types_list,
        'indexes': _indexes_dict,
        'columns': _columns_list,
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
