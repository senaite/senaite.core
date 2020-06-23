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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_COLUMNS
from bika.lims.catalog.catalog_basic_template import BASE_CATALOG_INDEXES
from bika.lims.interfaces import IBikaCatalogAnalysisRequestListing
from zope.interface import implements

# Using a variable to avoid plain strings in code
CATALOG_ANALYSIS_REQUEST_LISTING = "bika_catalog_analysisrequest_listing"

# Defining the indexes for this catalog
_indexes_dict = {
    # TODO: Can be removed? Same as id
    "sortable_title": "FieldIndex",
    "getClientUID": "FieldIndex",
    "getClientID": "FieldIndex",
    "getBatchUID": "FieldIndex",
    "getDateSampled": "DateIndex",
    "getSamplingDate": "DateIndex",
    "getDateReceived": "DateIndex",
    "getDateVerified": "DateIndex",
    "getDatePublished": "DateIndex",
    "getDueDate": "DateIndex",
    "getSampler": "FieldIndex",
    "getReceivedBy": "FieldIndex",
    "getPrinted": "FieldIndex",
    "getProvince": "FieldIndex",
    "getDistrict": "FieldIndex",
    "getClientSampleID": "FieldIndex",
    # To sort in lists
    "getClientTitle": "FieldIndex",
    "getPrioritySortkey": "FieldIndex",
    "assigned_state": "FieldIndex",
    # Searchable Text Index by wildcards
    # http://zope.readthedocs.io/en/latest/zope2book/SearchingZCatalog.html#textindexng
    "listing_searchable_text": "TextIndexNG3",
    "isRootAncestor": "BooleanIndex",
    "is_received": "BooleanIndex",
    "modified": "DateIndex",
}
# Defining the columns for this catalog
_columns_list = [
    "getCreatorFullName",
    "getCreatorEmail",
    "getPhysicalPath",
    # Used to create add an anchor to Sample ID that redirects to
    # the Sample view.
    "getClientOrderNumber",
    "getClientReference",
    "getClientSampleID",
    "getSampler",
    "getSamplerFullName",
    "getSamplerEmail",
    "getBatchUID",
    #  Used to print the ID of the Batch in lists
    "getBatchID",
    "getBatchURL",
    "getClientUID",
    "getClientTitle",
    "getClientID",
    "getClientURL",
    "getContactUID",
    "getContactUsername",
    "getContactEmail",
    "getContactURL",
    "getContactFullName",
    "getSampleTypeUID",
    "getSampleTypeTitle",
    # TODO Index "getSamplePointUID" is only used in reports/selection_macros
    "getSamplePointUID",
    "getSamplePointTitle",
    "getStorageLocationUID",
    "getStorageLocationTitle",
    "getSamplingDate",
    "getDateSampled",
    "getDateReceived",
    "getDateVerified",
    "getDatePublished",
    "getDescendantsUIDs",
    "getDistrict",
    "getProfilesUID",
    "getProfilesURL",
    "getProfilesTitle",
    "getProfilesTitleStr",
    "getRawParentAnalysisRequest",
    "getProvince",
    "getTemplateUID",
    "getTemplateURL",
    "getTemplateTitle",
    "getAnalysesNum",
    "getPrinted",
    "getSamplingDeviationTitle",
    "getPrioritySortkey",
    "getDueDate",
    "getInvoiceExclude",
    "getHazardous",
    "getSamplingWorkflowEnabled",
    "assigned_state",
    "getInternalUse",
    "getProgress",
]

# Adding basic indexes
_base_indexes_copy = BASE_CATALOG_INDEXES.copy()
_indexes_dict.update(_base_indexes_copy)
# Adding basic columns
_base_columns_copy = BASE_CATALOG_COLUMNS[:]
_columns_list += _base_columns_copy
# Defining the types for this catalog
_types_list = ["AnalysisRequest", ]

bika_catalog_analysisrequest_listing_definition = {
    # This catalog contains the metacolumns to list
    # analysisrequests in bikalisting
    CATALOG_ANALYSIS_REQUEST_LISTING: {
        "types": _types_list,
        "indexes": _indexes_dict,
        "columns": _columns_list,
    }
}


class BikaCatalogAnalysisRequestListing(BaseCatalog):
    """Catalog to list analysis requests
    """
    implements(IBikaCatalogAnalysisRequestListing)

    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ANALYSIS_REQUEST_LISTING,
                             "Catalog Analysis Request Listing",
                             "BikaCatalogAnalysisRequestListing")


InitializeClass(BikaCatalogAnalysisRequestListing)
