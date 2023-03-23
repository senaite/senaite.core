# -*- coding: utf-8 -*-

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import ILabelCatalog
from senaite.core.interfaces import IHaveLabels
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_label"
CATALOG_TITLE = "Senaite Label Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("labels", "", "KeywordIndex"),
    ("listing_searchable_text", "", "ZCTextIndex"),
]

COLUMNS = []


@implementer(ILabelCatalog)
class LabelCatalog(BaseCatalog):
    """Catalog for labeled objects
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    def is_obj_indexable(self, obj, portal_type, mapped_types):
        return IHaveLabels.providedBy(obj)


InitializeClass(LabelCatalog)
