# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import IAutoImportLogCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_autoimportlog"
CATALOG_TITLE = "Senaite Auto Import Log Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("getInstrumentUID", "", "FieldIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "getImportedFile",
    "getInstrumentTitle",
    "getInstrumentUrl",
    "getInterface",
    "getLogTime"
    "getResults",
]

TYPES = [
    # portal_type name
    "AutoImportLog"
]


@implementer(IAutoImportLogCatalog)
class AutoImportLogCatalog(BaseCatalog):
    """Catalog for AutoImportLog objects
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(AutoImportLogCatalog)
