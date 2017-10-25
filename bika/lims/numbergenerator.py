# -*- coding: utf-8 -*-

import thread
import logging
import datetime
from bika.lims.interfaces import INumberGenerator
from BTrees.OIBTree import OIBTree
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.component import getGlobalSiteManager
from zope.interface import implements



lock = thread.allocate_lock()

logger = logging.getLogger("bika.lims.idserver")

STORAGE_KEY  = "bika.lims.numbercounter"
STORAGE_HASH = "bika.lims.numbercounter.hash"

NUMBER_STORAGE = "bika.lims.consecutive_numbers_storage"


def get_storage_location():
    """ get the portal with the plone.api
    """
    location = api.portal.getSite()
    if location.get('bika_setup', False):
        location = location['bika_setup']
    return location

def get_portal_annotation():
    """ annotation storage bound to the portal
    """
    return IAnnotations(get_storage_location())


class NumberGenerator(object):
    """ perisistent consecutive numbers
    """
    implements(INumberGenerator)

    @property
    def storage(self):
        """ get the counter storage
        """
        annotation = get_portal_annotation()
        if annotation.get(NUMBER_STORAGE) is None:
            annotation[NUMBER_STORAGE]  = OIBTree()
        return annotation[NUMBER_STORAGE]

    def flush(self):
        """ delete all annotation storages
        """
        annotations = get_portal_annotation()
        if annotations.get(NUMBER_STORAGE) is not None:
            del annotations[NUMBER_STORAGE]

    def keys(self):
        out = []
        for key in self.storage.keys():
            out.append(key)
        return out

    def values(self):
        out = []
        for value in self.storage.values():
            out.append(value)
        return out

    def get_number(self, key):
        """ get the next consecutive number
        """
        storage = self.storage

        try:
            logger.debug("*** consecutive number lock acquire ***")
            lock.acquire()
            try:
                counter = storage[key]
                storage[key] = counter + 1
            except KeyError:
                storage[key] = 0
        finally:
            logger.debug("*** consecutive number lock release ***")
            self.storage._p_changed = True
            lock.release()

        logger.debug("NUMBER => %d" % storage[key])
        return storage[key]

    def generate_number(self, key="default"):
        """ get a number
        """
        return self.get_number(key)

    def __call__(self, key="default"):
        return self.generate_number(key)

