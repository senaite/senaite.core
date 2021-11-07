# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import ISetupCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_setup"
CATALOG_TITLE = "Senaite Setup Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("category_uid", "", "KeywordIndex"),
    ("department_id", "", "KeywordIndex"),
    ("department_title", "", "KeywordIndex"),
    ("department_uid", "", "KeywordIndex"),
    ("Description", "", "ZCTextIndex"),
    ("getClientUID", "", "FieldIndex"),
    ("getKeyword", "", "FieldIndex"),
    ("instrumenttype_title", "", "KeywordIndex"),
    ("instrument_title", "", "KeywordIndex"),
    ("listing_searchable_text", "", "ZCTextIndex"),
    ("method_available_uid", "", "KeywordIndex"),
    ("point_of_capture", "", "FieldIndex"),
    ("price", "", "FieldIndex"),
    ("price_total", "", "FieldIndex"),
    ("sampletype_title", "", "KeywordIndex"),
    ("sampletype_uid", "", "KeywordIndex"),
    ("sortable_title", "", "FieldIndex"),
    ("Title", "", "ZCTextIndex"),
    ("Type", "", "FieldIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "Description",
    "description",
    "getCategoryTitle",
    "getCategoryUID",
    "getClientUID",
    "getKeyword",
    "id",
    "path",
    "sortable_title",
    "title",
    "Type",
]

TYPES = [
    # portal_type name
]


@implementer(ISetupCatalog)
class SetupCatalog(BaseCatalog):
    """Catalog for setup objects
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(SetupCatalog)
