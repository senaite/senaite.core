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
    ("getDueDate", "getDueDate", "DateIndex"),
    ("listing_searchable_text", "", "ZCTextIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "getRequestID",
]

TYPES = [
    "AnalysisRequest"
]


@implementer(ISampleCatalog)
class SampleCatalog(BaseCatalog):
    """Catalog for sample objects
    """
    id = CATALOG_ID

    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title="Sample Catalog")


InitializeClass(SampleCatalog)
