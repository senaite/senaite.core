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

from senaite.core.tests.base import BaseTestCase
from senaite.core.upgrade.v02_07_000 import get_loaded_object
from ZODB.POSException import POSKeyError
from ZODB.POSException import ReadConflictError

PATH = "/plone/clients/client-1/W-0001"


class StoredObject(object):
    """An object whose stored state raises the given error when loaded
    """

    def __init__(self, error=None):
        self.error = error

    def _p_activate(self):
        if self.error:
            raise self.error


class Brain(object):
    """A catalog entry pointing to the given object
    """

    def __init__(self, obj):
        self.obj = obj

    def getObject(self):
        return self.obj

    def getPath(self):
        return PATH


class TestGetLoadedObject(BaseTestCase):
    """An upgrade step skips the objects whose stored state is damaged
    """

    def test_loadable_object(self):
        obj = StoredObject()
        self.assertIs(get_loaded_object(Brain(obj)), obj)

    def test_gone_object(self):
        self.assertIsNone(get_loaded_object(Brain(None)))

    def test_damaged_state(self):
        # what unpickling a damaged sample raised on a production database
        error = AttributeError("'dict' object has no attribute 'append'")
        brain = Brain(StoredObject(error))
        self.assertIsNone(get_loaded_object(brain))

    def test_missing_record(self):
        brain = Brain(StoredObject(POSKeyError("0x01")))
        self.assertIsNone(get_loaded_object(brain))

    def test_conflict_is_raised(self):
        # a conflict is no damage, the transaction has to be retried
        brain = Brain(StoredObject(ReadConflictError()))
        self.assertRaises(ReadConflictError, get_loaded_object, brain)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetLoadedObject))
    return suite
