# -*- coding: utf-8 -*-

import transaction
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import \
    manage_zcatalog_entries as ManageZCatalogEntries
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.class_init import InitializeClass
from bika.lims import api
from bika.lims import logger
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.ZCatalog.ZCatalog import ZCatalog
from senaite.core.interfaces import ISenaiteCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_base"
CATALOG_TITLE = "Senaite Base Catalog"

INDEXES = [
    # id, indexed attribute, type
    ("allowedRolesAndUsers", "", "KeywordIndex"),
    ("created", "", "DateIndex"),
    ("CreationDate", "", "DateIndex"),
    ("Creator", "", "FieldIndex"),
    ("getId", "", "FieldIndex"),
    ("id", "", "FieldIndex"),
    ("is_active", "", "BooleanIndex"),
    ("object_provides", "", "KeywordIndex"),
    ("path", "", "ExtendedPathIndex"),
    ("portal_type", "", "FieldIndex"),
    ("review_state", "", "FieldIndex"),
    ("title", "", "FieldIndex"),
    ("UID", "", "UUIDIndex"),
]

COLUMNS = [
    # attribute name
    "allowedRolesAndUsers",
    "created",
    "Creator",
    "getId",
    "meta_type",
    "portal_type",
    "review_state",
    "state_title",
    "Title",
    "UID",
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
        ZCatalog.__init__(self, id, title=title, **kw)

    @property
    def mapped_catalog_types(self):
        return TYPES

    def is_indexable(self, obj):
        """Checks if the object can be indexed
        """
        if not (base_hasattr(obj, "reindexObject")):
            return False
        if not (safe_callable(obj.reindexObject)):
            return False
        return True

    def get_portal_type(self, obj):
        """Returns the portal type of the object
        """
        if not api.is_object(obj):
            return None
        return api.get_portal_type(obj)

    def get_mapped_at_types(self):
        """Returns all mapped AT types from archetype_tool
        """
        at = api.get_tool("archetype_tool", default=None)
        if at is None:
            return []
        mapped_types = [k for k, v in at.catalog_map.items() if self.id in v]
        return mapped_types

    def get_mapped_types(self):
        """Returns the mapped types of this catalog

        :returns: list of catalog types + types mapped over archetype_tool
        """
        mapped_catalog_types = self.mapped_catalog_types
        mapped_at_types = self.get_mapped_at_types()
        return mapped_catalog_types + mapped_at_types

    @security.protected(ManageZCatalogEntries)
    def clearFindAndRebuild(self):
        """Considers only mapped types when reindexing the whole catalog
        """
        idxs = list(self.indexes())

        # porta types to consider for this catalog
        mapped_types = self.get_mapped_types()

        def indexObject(obj, path):
            __traceback_info__ = path

            # skip non-indexable types
            if not self.is_indexable(obj):
                return

            # get the porta type of this object
            portal_type = self.get_portal_type(obj)

            try:
                # only consider mapped types if we have them set
                if mapped_types and portal_type in mapped_types:
                    # NOTE: This method indexes only the object in this
                    #       catalog, but does not take DX multiplexing into
                    #       consideration.
                    self._reindexObject(obj, idxs=idxs)  # bypass queue
                    self.counter += 1
                elif api.is_dexterity_content(obj):
                    # NOTE: Catalog multiplexing is only available for DX types
                    #       and stores the catalogs in a variable `_catalogs`.
                    multiplex_catalogs = getattr(obj, "_catalogs", [])
                    if self.id in multiplex_catalogs:
                        self._reindexObject(obj, idxs=idxs)  # bypass queue
                        self.counter += 1
                else:
                    return
            except TypeError:
                # Catalogs have 'indexObject' as well, but they
                # take different args, and will fail
                pass

            if self.counter and self.counter % 100 == 0:
                logger.info("Progress: {} objects have been cataloged for {}."
                            .format(self.counter, self.id))
                transaction.savepoint(optimistic=True)

        logger.info("Cleaning and rebuilding catalog '%s'..." % self.id)
        self.counter = 0
        self.manage_catalogClear()
        portal = aq_parent(aq_inner(self))
        portal.ZopeFindAndApply(
            portal,
            search_sub=True,
            apply_func=indexObject
        )
        logger.info("Catalog '%s' cleaned and rebuilt" % self.id)


InitializeClass(BaseCatalog)
