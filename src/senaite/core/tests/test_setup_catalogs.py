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

from bika.lims import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.tests.base import DataTestCase
from senaite.core.upgrade.v02_07_000 import reindex_empty_index

INDEX = "sortable_title"


class TestSetupCoreCatalogs(DataTestCase):
    """Setting up the core catalogs indexes the existing content in a new index
    """

    def setUp(self):
        super(TestSetupCoreCatalogs, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_new_index_holds_the_existing_content(self):
        catalog = api.get_tool(SETUP_CATALOG)
        self.assertTrue(len(catalog) > 0)

        # an index that an upgrade adds to an existing catalog
        catalog.delIndex(INDEX)
        self.assertNotIn(INDEX, catalog.indexes())

        setup_core_catalogs(self.portal)

        index = catalog._catalog.getIndex(INDEX)
        self.assertEqual(index.numObjects(), len(catalog))

    def test_upgrade_reindexes_an_empty_index(self):
        catalog = api.get_tool(SETUP_CATALOG)
        index = catalog._catalog.getIndex(INDEX)

        # an index the upgrade left empty is reindexed
        index.clear()
        self.assertEqual(index.numObjects(), 0)
        reindex_empty_index(SETUP_CATALOG, INDEX)
        self.assertEqual(index.numObjects(), len(catalog))

        # an index that holds objects already is left as it is
        index.unindex_object(next(iter(index._unindex)))
        reindex_empty_index(SETUP_CATALOG, INDEX)
        self.assertEqual(index.numObjects(), len(catalog) - 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetupCoreCatalogs))
    return suite
