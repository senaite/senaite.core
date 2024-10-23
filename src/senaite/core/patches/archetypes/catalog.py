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

from bika.lims import api
from senaite.core.interfaces import IMultiCatalogBehavior
from plone.indexer.interfaces import IIndexableObject
from Products.ZCatalog.ZCatalog import ZCatalog
from senaite.core import logger
from senaite.core.catalog import AUDITLOG_CATALOG
from senaite.core.setuphandlers import CATALOG_MAPPINGS
from zope.component import queryMultiAdapter

PORTAL_CATALOG = "portal_catalog"
CATALOG_MAP = dict(CATALOG_MAPPINGS)


def is_auditlog_enabled():
    setup = api.get_senaite_setup()
    if not setup:
        return False
    return setup.getEnableGlobalAuditlog()


def catalog_object(self, object, uid=None, idxs=None,
                   update_metadata=1, pghandler=None):

    # Never catalog temporary objects
    if api.is_temporary(object):
        return

    # skip indexing auditlog catalog if disabled
    if self.id == AUDITLOG_CATALOG:
        if not is_auditlog_enabled():
            return

    if idxs is None:
        idxs = []
    self._increment_counter()

    w = object
    if not IIndexableObject.providedBy(object):
        # This is the CMF 2.2 compatible approach, which should be used
        # going forward
        wrapper = queryMultiAdapter((object, self), IIndexableObject)
        if wrapper is not None:
            w = wrapper

    ZCatalog.catalog_object(self, w, uid, idxs,
                            update_metadata, pghandler=pghandler)


def in_portal_catalog(obj):
    """Check if the given object should be indexed in portal catalog
    """
    # catalog objects appeared here?
    if not api.is_object(obj):
        return False

    # already handled in our catalog multiplex processor
    if IMultiCatalogBehavior.providedBy(obj):
        # BBB: Fallback for unset catalogs mapping, e.g. for DataBoxes
        catalogs = getattr(obj, "_catalogs", [])
        if len(catalogs) == 0:
            return True
        return False

    # check our static mapping from setuphandlers
    portal_type = api.get_portal_type(obj)
    catalogs = CATALOG_MAP.get(portal_type)
    if isinstance(catalogs, list) and PORTAL_CATALOG not in catalogs:
        return False

    # check archetype tool if we have an AT content type
    if api.is_at_type(obj):
        att = api.get_tool("archetype_tool", default=None)
        catalogs = att.catalog_map.get(portal_type) if att else None
        if isinstance(catalogs, list) and PORTAL_CATALOG not in catalogs:
            return False

    # all other contents (folders etc.) can be indexed in portal_catalog
    return True


def portal_catalog_index(self, obj, attributes=None):
    if not in_portal_catalog(obj):
        return
    path = api.get_path(obj)
    logger.info("Indexing object on path '%s' in portal_catalog" % path)
    pc = api.get_tool("portal_catalog")
    pc._indexObject(obj)


def portal_catalog_reindex(self, obj, attributes=None, update_metadata=1):
    if not in_portal_catalog(obj):
        return
    path = api.get_path(obj)
    logger.info("Reindexing object on path '%s' in portal_catalog" % path)
    pc = api.get_tool("portal_catalog")
    pc._reindexObject(obj, idxs=attributes, update_metadata=update_metadata)


def portal_catalog_unindex(self, obj):
    if not in_portal_catalog(obj):
        return
    path = api.get_path(obj)
    logger.info("Unindexing object on path '%s' in portal_catalog" % path)
    pc = api.get_tool("portal_catalog")
    pc._unindexObject(obj)
