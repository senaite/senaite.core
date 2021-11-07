# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import ISampleCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_sample_catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("sortable_title", "sortable_title", "FieldIndex"),
    # https://zope.readthedocs.io/en/latest/zopebook/SearchingZCatalog.html
    ("listing_searchable_text", "", "ZCTextIndex"),
    ("sortable_title", "", "FieldIndex"),
    ("getClientUID", "", "FieldIndex"),
    ("getClientID", "", "FieldIndex"),
    ("getBatchUID", "", "FieldIndex"),
    ("getDateSampled", "", "DateIndex"),
    ("getSamplingDate", "", "DateIndex)",
    ("getDateReceived", "", "DateIndex"),
    ("getDateVerified", "", "DateIndex"),
    ("getDatePublished", "", "DateIndex"),
    ("getDueDate", "", "DateIndex"),
    ("getSampler", "", "FieldIndex"),
    ("getReceivedBy", "", "FieldIndex"),
    ("getPrinted", "", "FieldIndex"),
    ("getProvince", "", "FieldIndex"),
    ("getDistrict", "", "FieldIndex"),
    ("getClientSampleID", "", "FieldIndex"),
    ("getClientTitle", "", "FieldIndex"),
    ("getPrioritySortkey", "", "FieldIndex"),
    ("assigned_state", "", "FieldIndex"),
    ("isRootAncestor", "", "BooleanIndex"),
    ("is_received", "", "BooleanIndex"),
    ("modified", "", "DateIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "getCreatorFullName",
    "getCreatorEmail",
    "getPhysicalPath",
    # Used to build an anchor to Sample ID that redirects to the Sample view.
    "getClientOrderNumber",
    "getClientReference",
    "getClientSampleID",
    "getSampler",
    "getSamplerFullName",
    "getSamplerEmail",
    "getBatchUID",
    # Used to print the ID of the Batch in lists
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

TYPES = [
    # portal_type name
    "AnalysisRequest",
]


@implementer(ISampleCatalog)
class SampleCatalog(BaseCatalog):
    """Catalog for sample objects
    """
    id = CATALOG_ID

    def __init__(self):
        self._mapped_types = TYPES
        BaseCatalog.__init__(self, CATALOG_ID, title="Sample Catalog")


InitializeClass(SampleCatalog)
