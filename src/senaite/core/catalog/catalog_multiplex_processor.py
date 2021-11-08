# -*- coding: utf-8 -*-

from Acquisition import aq_base
from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import IMultiCatalogBehavior
from Products.CMFCore.interfaces import IPortalCatalogQueueProcessor
from senaite.core.catalog import AUDITLOG_CATALOG
from zope.interface import implementer

REQUIRED_CATALOGS = [
    AUDITLOG_CATALOG,
]


@implementer(IPortalCatalogQueueProcessor)
class CatalogMultiplexProcessor(object):
    """A catalog multiplex processor
    """

    def get_catalogs_for(self, obj):
        catalogs = getattr(obj, "_catalogs", [])
        for rc in REQUIRED_CATALOGS:
            if rc in catalogs:
                continue
            catalogs.append(rc)
        return map(api.get_tool, catalogs)

    def supports_multi_catalogs(self, obj):
        """Check if the Multi Catalog Behavior is enabled
        """
        if IMultiCatalogBehavior(obj, None) is None:
            return False
        return True

    def index(self, obj, attributes=None):
        if attributes is None:
            attributes = []

        if not self.supports_multi_catalogs(obj):
            return

        catalogs = self.get_catalogs_for(obj)
        url = api.get_path(obj)

        for catalog in catalogs:
            logger.info(
                "CatalogMultiplexProcessor::indexObject:catalog={} url={}"
                .format(catalog.id, url))
            # We want the intersection of the catalogs idxs
            # and the incoming list.
            indexes = set(catalog.indexes()).intersection(attributes)
            # Skip reindexing if no indexes match
            if attributes and not indexes:
                continue
            # recatalog the object
            catalog.catalog_object(obj, url, idxs=list(indexes))

    def reindex(self, obj, attributes=None, update_metadata=1):
        # XXX: Do we need the additional `update_metadata` parameter?
        self.index(obj, attributes)

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
                catalog.uncatalog_object(url)

    def begin(self):
        pass

    def commit(self):
        pass

    def abort(self):
        pass
