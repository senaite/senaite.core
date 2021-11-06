# -*- coding: utf-8 -*-

from Products.CMFPlone.CatalogTool import CatalogTool
from AccessControl import ClassSecurityInfo
from Products.ZCatalog.ZCatalog import ZCatalog
from zope.interface import implementer
from senaite.core.interfaces import ISenaiteCatalog

CATALOG_ID = "senaite_catalog"

INDEXES = [
    # id, indexed attribute, type
    ("id", "", "FieldIndex"),
    ("title", "", "FieldIndex"),
    ("getId", "", "FieldIndex"),
    ("portal_type", "", "FieldIndex"),
    ("object_provides", "", "KeywordIndex"),
    ("UID", "", "UUIDIndex"),
    ("created", "", "DateIndex"),
    ("CreationDate", "", "DateIndex"),
    ("Creator", "", "FieldIndex"),
    ("allowedRolesAndUsers", "", "KeywordIndex"),
    ("review_state", "", "FieldIndex"),
    ("path", "", "ExtendedPathIndex"),
    ("is_active", "", "BooleanIndex"),
]

COLUMNS = [
    # attribute name
    "UID",
    "getId",
    "meta_type",
    "Title",
    "review_state",
    "state_title",
    "portal_type",
    "allowedRolesAndUsers",
    "created",
    "Creator",
]

TYPES = [
    # portal type name
]


@implementer(ISenaiteCatalog)
class BaseCatalog(CatalogTool):
    """Parent class for Senaite catalogs
    """
    security = ClassSecurityInfo()
    zmi_icon = "fas fa-book"

    def __init__(self, id, title="", **kw):
        # CatalogTool does not take any parameters in __init__
        ZCatalog.__init__(self, self.getId(), title=title, **kw)
