# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import IWorksheetCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_worksheet"
CATALOG_TITLE = "Senaite Worksheet Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("getAnalysesUIDs", "", "KeywordIndex"),
    ("getAnalyst", "", "FieldIndex"),
    ("getWorksheetTemplateTitle", "", "FieldIndex"),
    ("listing_searchable_text", "", "ZCTextIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "getAnalysesUIDs",
    "getAnalyst",
    "getNumberOfQCAnalyses",
    "getNumberOfRegularAnalyses",
    "getNumberOfRegularSamples",
    "getProgressPercentage",
    "getWorksheetTemplateTitle",
    "getWorksheetTemplateUID",
    "getWorksheetTemplateURL",
]

TYPES = [
    # portal_type name
    "Worksheet",
]


@implementer(IWorksheetCatalog)
class WorksheetCatalog(BaseCatalog):
    """Catalog for Worksheet objects
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(WorksheetCatalog)
