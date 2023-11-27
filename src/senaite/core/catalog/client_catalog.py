# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import IClientCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_client"
CATALOG_TITLE = "Senaite Client Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("Title", "", "ZCTextIndex"),  # needed for reference fields
    ("client_searchable_text", "", "ZCTextIndex"),
    ("getName", "", "FieldIndex"),
    ("sortable_title", "", "FieldIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "getClientID",
    "getName",
    "getEmailAddress",  # used in reference widget columns
]

TYPES = [
    # portal_type name
    "Client",
]


@implementer(IClientCatalog)
class ClientCatalog(BaseCatalog):
    """Catalog for client objects
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(ClientCatalog)
