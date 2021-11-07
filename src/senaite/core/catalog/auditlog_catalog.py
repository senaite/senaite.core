# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import IAuditlogCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_auditlog"
CATALOG_TITLE = "Senaite Auditlog Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("action", "", "FieldIndex"),
    ("actor", "", "FieldIndex"),
    ("listing_searchable_text", "", "ZCTextIndex"),
    ("modified", "", "DateIndex"),
    ("modifiers", "", "KeywordIndex"),
    ("snapshot_created", "", "DateIndex"),
    ("snapshot_version", "", "FieldIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
]

TYPES = [
    # portal_type name
]


@implementer(IAuditlogCatalog)
class AuditlogCatalog(BaseCatalog):
    """Catalog for auditlog objects
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(AuditlogCatalog)
