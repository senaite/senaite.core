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

import thread

from bika.lims import logger
from BTrees.OIBTree import OIBTree
from plone import api
from senaite.core.interfaces import INumberGenerator
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements

lock = thread.allocate_lock()

STORAGE_KEY = "bika.lims.numbercounter"
NUMBER_STORAGE = "bika.lims.consecutive_numbers_storage"


def get_portal():
    return api.portal.getSite()


def get_storage_location():
    """ get the portal with the plone.api
    """
    location = get_portal()
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
            annotation[NUMBER_STORAGE] = OIBTree()
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

    def __iter__(self):
        return self.storage.__iter__()

    def __getitem__(self, key):
        return self.storage.__getitem__(key)

    def get(self, key, default=None):
        return self.storage.get(key, default)

    def get_number(self, key):
        """ get the next consecutive number
        """
        logger.debug("NUMBER before => %s" % self.storage.get(key, '-'))
        try:
            logger.debug("*** consecutive number lock acquire ***")
            lock.acquire()
            try:
                counter = self.storage[key]
                self.storage[key] = counter + 1
            except KeyError:
                self.storage[key] = 1
        finally:
            logger.debug("*** consecutive number lock release ***")
            lock.release()

        logger.debug("NUMBER after => %s" % self.storage.get(key, '-'))
        return self.storage[key]

    def set_number(self, key, value):
        """ set a key's value
        """
        if not isinstance(value, int):
            logger.error("set_number: Value must be an integer")
            return
        try:
            lock.acquire()
            self.storage[key] = value
        finally:
            lock.release()

        return self.storage[key]

    def generate_number(self, key="default"):
        """ get a number
        """
        return self.get_number(key)

    def __call__(self, key="default"):
        return self.generate_number(key)
