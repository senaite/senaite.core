# -*- coding: utf-8 -*-

from bika.lims import api
from plone.indexer.interfaces import IIndexableObject
from Products.ZCatalog.ZCatalog import ZCatalog
from senaite.core.catalog import AUDITLOG_CATALOG
from zope.component import queryMultiAdapter


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
