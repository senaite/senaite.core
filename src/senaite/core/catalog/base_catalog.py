# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from threading import RLock

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
from senaite.core.interfaces import ISenaiteCatalogObject
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_base"
CATALOG_TITLE = "Senaite Base Catalog"

progress_rlock = RLock()

INDEXES = [
    # id, indexed attribute, type
    ("allowedRolesAndUsers", "", "KeywordIndex"),
    ("created", "", "DateIndex"),
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
    "Creator",
    "Description",  # used ind default reference widget columns
    "Title",  # used in default reference widget columns
    "UID",
    "allowedRolesAndUsers",
    "created",
    "getId",
    "meta_type",
    "portal_type",
    "review_state",
    "state_title",
]

TYPES = [
    # portal type name
]


@implementer(ISenaiteCatalogObject)
class BaseCatalog(CatalogTool):
    """Parent class for Senaite catalogs
    """
    security = ClassSecurityInfo()
    zmi_icon = "fas fa-book"

    def __init__(self, id, title="", **kw):
        # CatalogTool does not take any parameters in __init__
        ZCatalog.__init__(self, id, title=title, **kw)
        self.progress_counter = 0

    @property
    def mapped_catalog_types(self):
        return TYPES

    def supports_indexing(self, obj):
        """Checks if the object can be indexed
        """
        if not (base_hasattr(obj, "reindexObject")):
            return False
        if not (safe_callable(obj.reindexObject)):
            return False
        return True

    def is_obj_indexable(self, obj, portal_type, mapped_types):
        """Checks if the object can be indexed
        """
        if portal_type in mapped_types:
            return True
        if api.is_dexterity_content(obj):
            multiplex_catalogs = getattr(obj, "_catalogs", [])
            return self.id in multiplex_catalogs
        return False

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
        all_types = set(mapped_catalog_types + mapped_at_types)
        return list(all_types)

    def log_progress(self):
        """Log reindex progress
        """
        with progress_rlock:
            self.progress_counter += 1

        if self.progress_counter % 100 == 0:
            logger.info("Progress: {} objects have been cataloged for {}."
                        .format(self.progress_counter, self.id))

        if self.progress_counter % 10000 == 0:
            logger.info("Creating transaction savepoint after {} objects"
                        .format(self.progress_counter))
            transaction.savepoint(optimistic=True)

    def deactivate_object(self, obj):
        """Deactivate the object to save memory
        """
        try:
            obj._p_deactivate()
        except AttributeError:
            pass

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
            if not self.supports_indexing(obj):
                return

            # get the porta type of this object
            portal_type = self.get_portal_type(obj)

            try:
                # only consider mapped types if we have them set
                if self.is_obj_indexable(obj, portal_type, mapped_types):
                    self._reindexObject(obj, idxs=idxs)  # bypass queue
                    self.log_progress()
                # flush object from memory
                self.deactivate_object(obj)
            except TypeError:
                # Catalogs have 'indexObject' as well, but they
                # take different args, and will fail
                pass

        # reset the progress counter
        self.progress_counter = 0

        logger.info("Cleaning and rebuilding catalog '%s'..." % self.id)
        self.manage_catalogClear()
        portal = aq_parent(aq_inner(self))
        portal.ZopeFindAndApply(
            portal,
            search_sub=True,
            apply_func=indexObject
        )
        logger.info("Catalog '%s' cleaned and rebuilt" % self.id)


InitializeClass(BaseCatalog)
