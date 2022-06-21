# -*- coding: utf-8 -*-

from plone.indexer.interfaces import IIndexableObject
from Products.ZCatalog.ZCatalog import ZCatalog
from zope.component import queryMultiAdapter


def catalog_object(self, object, uid=None, idxs=None,
                   update_metadata=1, pghandler=None):

    try:
        # Never catalog temporary objects
        temporary = object.isTemporary()
        if temporary is True:
            return
    except AttributeError:
        pass

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
