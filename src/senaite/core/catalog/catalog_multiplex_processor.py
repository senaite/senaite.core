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

from Acquisition import aq_base
from bika.lims import api
from bika.lims import logger
from Products.CMFCore.interfaces import IPortalCatalogQueueProcessor
from senaite.core.catalog import AUDITLOG_CATALOG
from senaite.core.interfaces import IMultiCatalogBehavior
from zope.interface import implementer

REQUIRED_CATALOGS = [
    AUDITLOG_CATALOG,
]


@implementer(IPortalCatalogQueueProcessor)
class CatalogMultiplexProcessor(object):
    """A catalog multiplex processor
    """

    def is_global_auditlog_enabled(self):
        """Check if the global auditlogging is enabled
        """
        setup = api.get_senaite_setup()
        # might happen during installation
        if not setup:
            return False
        return setup.getEnableGlobalAuditlog()

    def get_catalogs_for(self, obj):
        """Get a list of catalog IDs for the given object
        """
        # get a list of catalog IDs that are mapped to the object
        catalogs = list(map(lambda x: x.id, api.get_catalogs_for(obj)))

        for rc in REQUIRED_CATALOGS:
            if rc in catalogs:
                continue
            catalogs.append(rc)

        # remove auditlog catalog if disabled
        if not self.is_global_auditlog_enabled():
            catalogs = filter(lambda cid: cid != AUDITLOG_CATALOG, catalogs)

        return map(api.get_tool, catalogs)

    def supports_multi_catalogs(self, obj):
        """Check if the Multi Catalog Behavior is enabled
        """
        if api.is_temporary(obj):
            return False
        if api.is_dexterity_content(obj) and \
           IMultiCatalogBehavior(obj, None) is None:
            return False
        return True

    def index(self, obj, attributes=None):
        if not self.supports_multi_catalogs(obj):
            return

        catalogs = self.get_catalogs_for(obj)
        url = api.get_path(obj)

        for catalog in catalogs:
            logger.info(
                "CatalogMultiplexProcessor::indexObject:catalog={} url={}"
                .format(catalog.id, url))
            catalog._indexObject(obj)

    def reindex(self, obj, attributes=None, update_metadata=1):
        if attributes is None:
            attributes = []

        if not self.supports_multi_catalogs(obj):
            return

        catalogs = self.get_catalogs_for(obj)
        url = api.get_path(obj)

        for catalog in catalogs:
            logger.info(
                "CatalogMultiplexProcessor::reindexObject:catalog={} url={}"
                .format(catalog.id, url))
            # Intersection of the catalogs indexes and the incoming attributes
            indexes = list(set(catalog.indexes()).intersection(attributes))
            catalog._reindexObject(
                obj, idxs=indexes, update_metadata=update_metadata)

    def unindex(self, obj):
        wrapped_obj = obj
        if aq_base(obj).__class__.__name__ == "PathWrapper":
            # Could be a PathWrapper object from collective.indexing.
            obj = obj.context

        if not self.supports_multi_catalogs(obj):
            return

        catalogs = self.get_catalogs_for(obj)
        # get the old path from the wrapped object
        url = api.get_path(wrapped_obj)

        for catalog in catalogs:
            if catalog._catalog.uids.get(url, None) is not None:
                logger.info(
                    "CatalogMultiplexProcessor::unindex:catalog={} url={}"
                    .format(catalog.id, url))
                catalog._unindexObject(wrapped_obj)

    def begin(self):
        pass

    def commit(self):
        pass

    def abort(self):
        pass
