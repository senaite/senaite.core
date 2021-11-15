# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import IReportCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_report"
CATALOG_TITLE = "Senaite Report Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("getClientUID", "", "FieldIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "getClientTitle"
    "getClientURL",
    "getCreatorFullName",
    "getFileSize",
]

TYPES = [
    # portal_type name
    "Report",
]


@implementer(IReportCatalog)
class ReportCatalog(BaseCatalog):
    """Catalog for report objects
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(ReportCatalog)
