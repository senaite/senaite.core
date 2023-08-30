# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import IContactCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_contact"
CATALOG_TITLE = "Senaite Contact Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("Title", "", "ZCTextIndex"),  # needed for reference fields
    ("listing_searchable_text", "", "ZCTextIndex"),
    ("getFullname", "", "FieldIndex"),
    ("getParentUID", "", "FieldIndex"),
    ("getUsername", "", "FieldIndex"),
    ("sortable_title", "", "FieldIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
]

TYPES = [
    # portal_type name
    "Contact",
    "LabContact",
    "SupplierContact",
]


@implementer(IContactCatalog)
class ContactCatalog(BaseCatalog):
    """Catalog for contact objects
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(ContactCatalog)
