# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import ISenaiteCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog"
CATALOG_TITLE = "Senaite Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("listing_searchable_text", "", "ZCTextIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
]

TYPES = [
    # portal_type name
]


@implementer(ISenaiteCatalog)
class SenaiteCatalog(BaseCatalog):
    """Catalog for Senaite LIMS
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(SenaiteCatalog)
