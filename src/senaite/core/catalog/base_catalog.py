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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from threading import RLock

import transaction
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import \
    manage_zcatalog_entries as ManageZCatalogEntries
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.class_init import InitializeClass
from Missing import Value as MV
from plone.indexer.interfaces import IIndexableObject
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.ZCatalog.ZCatalog import ZCatalog
from senaite.core import logger
from senaite.core.interfaces import ISenaiteCatalogObject
from zope.component import queryMultiAdapter
from zope.interface import implementer

# NOTE: `bika.lims` is imported lazily inside functions to avoid a
# circular import: `senaite.core.catalog.__init__` pulls in this module
# via `analysis_catalog`, and `bika/lims/__init__.py` re-enters
# `senaite.core.catalog` through `bika.lims.catalog`.

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

    def catalog_object(self, object, uid=None, idxs=None, update_metadata=1,
                       pghandler=None):
        """Catalog the object, optionally refreshing only some metadata.

        `update_metadata` keeps its usual boolean meaning, but may also be a
        list/tuple/set of metadata column names. In that case ZCatalog's
        wholesale metadata recompute is skipped: only the named columns are
        recomputed and spliced into the stored record, which avoids re-running
        every (potentially expensive) metadata accessor when a caller only
        needs a few columns refreshed (e.g. a targeted reindex in an upgrade
        step).

        When a column list is given, an empty/None `idxs` means *do not touch
        any index* (instead of ZCatalog's "all indexes"), so a caller can
        refresh metadata columns without reindexing.
        """
        if not isinstance(update_metadata, (list, tuple, set)):
            return CatalogTool.catalog_object(
                self, object, uid=uid, idxs=idxs,
                update_metadata=update_metadata, pghandler=pghandler)

        columns = [col for col in update_metadata if col]
        # Only reindex when specific indexes were requested.
        if idxs:
            CatalogTool.catalog_object(
                self, object, uid=uid, idxs=idxs, update_metadata=0,
                pghandler=pghandler)
        if columns:
            self.refresh_catalog_metadata(object, uid, columns)
        return None

    def refresh_catalog_metadata(self, object, uid, columns):
        """Recompute only `columns` in the stored metadata record of `object`

        Reads the existing record, recomputes the requested columns from the
        object (wrapped so `plone.indexer` adapters provide the values, exactly
        as `recordify` would) and writes the record back. Falls back to a full
        record when the object has no metadata yet.
        """
        zcatalog = self._catalog
        if uid is None:
            uid = "/".join(object.getPhysicalPath())
        rid = zcatalog.uids.get(uid)
        if rid is None:
            return

        # Wrap so plone.indexer adapters provide the metadata values
        wrapped = object
        if not IIndexableObject.providedBy(object):
            wrapper = queryMultiAdapter((object, self), IIndexableObject)
            if wrapper is not None:
                wrapped = wrapper

        record = zcatalog.data.get(rid)
        if record is None:
            # Freshly indexed without metadata; build the full record so the
            # object is not left without any metadata.
            zcatalog.data[rid] = zcatalog.recordify(wrapped)
            return

        new_record = list(record)
        schema = zcatalog.schema
        for column in columns:
            position = schema.get(column)
            if position is None:
                continue
            value = getattr(wrapped, column, MV)
            if value is not MV and safe_callable(value):
                value = value()
            new_record[position] = value
        zcatalog.data[rid] = tuple(new_record)

    def _listAllowedRolesAndUsers(self, user):
        """Extend the base allowed-roles list with the asking user's
        linked client token.

        Client-tree content carries a stable ``client:<client_uid>``
        token in its ``allowedRolesAndUsers`` index (see
        ``senaite.core.catalog.indexer.allowedrolesandusers``). For
        every catalog query we look up the user's
        ``linked_client_uid`` member property (set when a client
        contact is linked to the user) and inject the matching
        ``client:<uid>`` token, so client users see their client's
        content without any persistent local role or group.
        """
        result = super(BaseCatalog, self)._listAllowedRolesAndUsers(user)
        try:
            client_uid = user.getProperty("linked_client_uid", "") or ""
        except Exception as exc:
            # A broken `getProperty` would silently strip the
            # client-token from every query and lock the linked
            # user out of their own data. Log loud enough to be
            # traceable, but keep the query itself working.
            logger.debug(
                "linked_client_uid lookup failed on user %r: %s"
                % (user, exc))
            client_uid = ""
        if client_uid:
            result.append("client:" + client_uid)
        return result

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
        from bika.lims import api
        if portal_type in mapped_types:
            return True
        if api.is_dexterity_content(obj):
            multiplex_catalogs = getattr(obj, "_catalogs", [])
            return self.id in multiplex_catalogs
        return False

    def get_portal_type(self, obj):
        """Returns the portal type of the object
        """
        from bika.lims import api
        if not api.is_object(obj):
            return None
        return api.get_portal_type(obj)

    def get_mapped_at_types(self):
        """Returns all mapped AT types from archetype_tool
        """
        from bika.lims import api
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
