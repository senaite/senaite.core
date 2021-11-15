
# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import IAnalysisCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_analysis"
CATALOG_TITLE = "Senaite Analysis Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("getAnalyst", "", "FieldIndex"),
    ("getAncestorsUIDs", "", "KeywordIndex"),
    ("getCategoryUID", "", "FieldIndex"),
    ("getClientTitle", "", "FieldIndex"),
    ("getClientUID", "", "FieldIndex"),
    ("getDateReceived", "", "DateIndex"),
    ("getDueDate", "", "DateIndex"),
    ("getInstrumentUID", "", "FieldIndex"),
    ("getKeyword", "", "FieldIndex"),
    ("getPointOfCapture", "", "FieldIndex"),
    ("getPrioritySortkey", "", "FieldIndex"),
    ("getReferenceAnalysesGroupID", "", "FieldIndex"),
    ("getRequestID", "", "FieldIndex"),
    ("getResultCaptureDate", "", "DateIndex"),
    ("getSampleTypeUID", "", "FieldIndex"),
    ("getServiceUID", "", "FieldIndex"),
    ("getWorksheetUID", "", "FieldIndex"),
    ("isSampleReceived", "", "BooleanIndex"),
    ("sortable_title", "", "FieldIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "getAnalysisPortalType",
    "getAnalyst",
    "getAnalystName",
    "getCategoryTitle",
    "getClientOrderNumber",
    "getClientTitle",
    "getClientURL",
    "getDateReceived",
    "getDateSampled",
    "getDueDate",
    "getKeyword",
    "getLastVerificator",
    "getMethodTitle",
    "getMethodURL",
    "getNumberOfRequiredVerifications",
    "getNumberOfVerifications",
    "getParentURL",
    "getPrioritySortkey",
    "getReferenceAnalysesGroupID",
    "getReferenceResults",
    "getRemarks",
    "getRequestID",
    "getRequestTitle",
    "getRequestURL",
    "getResult",
    "getResultCaptureDate",
    "getResultOptions",
    "getRetestOfUID",
    "getSampleTypeUID",
    "getServiceUID",
    "getSubmittedBy",
    "getUnit",
    "getVerificators",
    "isSelfVerificationEnabled",
]

TYPES = [
    # portal_type name
    "Analysis",
    "ReferenceAnalysis",
    "DuplicateAnalysis",
]


@implementer(IAnalysisCatalog)
class AnalysisCatalog(BaseCatalog):
    """Catalog for analysis objects
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(AnalysisCatalog)
