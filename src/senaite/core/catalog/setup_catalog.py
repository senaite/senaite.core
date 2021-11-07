# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import ISetupCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_setup_catalog"
CATALOG_TITLE = "Setup Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("Description", "", "ZCTextIndex"),
    ("Title", "", "ZCTextIndex"),
    ("Type", "", "FieldIndex"),
    ("category_uid", "", "KeywordIndex"),
    ("department_title", "", "KeywordIndex"),
    ("department_uid", "", "KeywordIndex"),
    ("department_id", "", "KeywordIndex"),
    ("getClientUID", "", "FieldIndex"),
    ("getKeyword", "", "FieldIndex"),
    ("instrument_title", "", "KeywordIndex"),
    ("instrumenttype_title", "", "KeywordIndex"),
    ("listing_searchable_text", "", "ZCTextIndex"),
    ("method_available_uid", "", "KeywordIndex"),
    ("point_of_capture", "", "FieldIndex"),
    ("price", "", "FieldIndex"),
    ("price_total", "", "FieldIndex"),
    ("sampletype_title", "", "KeywordIndex"),
    ("sampletype_uid", "", "KeywordIndex"),
    ("sortable_title", "", "FieldIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "path",
    "id",
    "Type",
    "Description",
    "title",
    "sortable_title",
    "description",
    "getCategoryTitle",
    "getCategoryUID",
    "getClientUID",
    "getKeyword",
]

TYPES = [
    # portal_type name
]


@implementer(ISetupCatalog)
class SetupCatalog(BaseCatalog):
    """Catalog for setup objects
    """
    id = CATALOG_ID

    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(SetupCatalog)
