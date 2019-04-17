# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool as BaseCatalog
from bika.lims.interfaces import IAuditLogCatalog
from zope.interface import implements


# Using a variable to avoid plain strings in code
CATALOG_AUDITLOG = "auditlog_catalog"

# Defining the indexes for this catalog
_indexes = {
    "title": "FieldIndex",
    "getId": "FieldIndex",
    "portal_type": "FieldIndex",
    "object_provides": "KeywordIndex",
    "UID": "UUIDIndex",
    "review_state": "FieldIndex",
    "is_active": "BooleanIndex",
    "modified": "DateIndex",
    "modifiers": "KeywordIndex",
    "actor": "FieldIndex",
    "action": "FieldIndex",
    "listing_searchable_text": "TextIndexNG3",
    "snapshot_created": "DateIndex",
    "snapshot_version": "FieldIndex",
    "path": "PathIndex",
}
# Defining the columns for this catalog
_columns = []
# Defining the types for this catalog
_types = []

catalog_auditlog_definition = {
    CATALOG_AUDITLOG: {
        "types": _types,
        "indexes": _indexes,
        "columns": _columns,
    }
}


class AuditLogCatalog(BaseCatalog):
    """Audit Log Catalog
    """
    implements(IAuditLogCatalog)

    def __init__(self):
        BaseCatalog.__init__(
            self, CATALOG_AUDITLOG, "Audit Log Catalog", "AuditLogCatalog")


InitializeClass(AuditLogCatalog)
