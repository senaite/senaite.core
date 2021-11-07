# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import ISampleCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_sample"
CATALOG_TITLE = "Senaite Sample Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("assigned_state", "", "FieldIndex"),
    ("getBatchUID", "", "FieldIndex"),
    ("getClientID", "", "FieldIndex"),
    ("getClientSampleID", "", "FieldIndex"),
    ("getClientTitle", "", "FieldIndex"),
    ("getClientUID", "", "FieldIndex"),
    ("getDatePublished", "", "DateIndex"),
    ("getDateReceived", "", "DateIndex"),
    ("getDateSampled", "", "DateIndex"),
    ("getDateVerified", "", "DateIndex"),
    ("getDistrict", "", "FieldIndex"),
    ("getDueDate", "", "DateIndex"),
    ("getPrinted", "", "FieldIndex"),
    ("getPrioritySortkey", "", "FieldIndex"),
    ("getProvince", "", "FieldIndex"),
    ("getReceivedBy", "", "FieldIndex"),
    ("getSampler", "", "FieldIndex"),
    ("getSamplingDate", "", "DateIndex"),
    ("isRootAncestor", "", "BooleanIndex"),
    ("is_received", "", "BooleanIndex"),
    # https://zope.readthedocs.io/en/latest/zopebook/SearchingZCatalog.html
    ("listing_searchable_text", "", "ZCTextIndex"),
    ("modified", "", "DateIndex"),
    ("sortable_title", "", "FieldIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "assigned_state",
    "getAnalysesNum",
    "getBatchID",
    "getBatchUID",
    "getBatchURL",
    "getClientID",
    "getClientOrderNumber",
    "getClientReference",
    "getClientSampleID",
    "getClientTitle",
    "getClientUID",
    "getClientURL",
    "getContactEmail",
    "getContactFullName",
    "getContactUID",
    "getContactURL",
    "getContactUsername",
    "getCreatorEmail",
    "getCreatorFullName",
    "getDatePublished",
    "getDateReceived",
    "getDateSampled",
    "getDateVerified",
    "getDescendantsUIDs",
    "getDistrict",
    "getDueDate",
    "getHazardous",
    "getInternalUse",
    "getInvoiceExclude",
    "getPhysicalPath",
    "getPrinted",
    "getPrioritySortkey",
    "getProfilesTitle",
    "getProfilesTitleStr",
    "getProfilesUID",
    "getProfilesURL",
    "getProgress",
    "getProvince",
    "getRawParentAnalysisRequest",
    "getSamplePointTitle",
    "getSampler",
    "getSamplerEmail",
    "getSamplerFullName",
    "getSampleTypeTitle",
    "getSampleTypeUID",
    "getSamplingDate",
    "getSamplingDeviationTitle",
    "getSamplingWorkflowEnabled",
    "getStorageLocationTitle",
    "getStorageLocationUID",
    "getTemplateTitle",
    "getTemplateUID",
    "getTemplateURL",
]

TYPES = [
    # portal_type name
    "AnalysisRequest",
]


@implementer(ISampleCatalog)
class SampleCatalog(BaseCatalog):
    """Catalog for sample objects
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(SampleCatalog)
