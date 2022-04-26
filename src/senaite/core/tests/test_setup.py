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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFPlone.utils import get_installer
from senaite.core.tests.base import BaseTestCase


class TestSetup(BaseTestCase):
    """Test Setup
    """

    def test_is_senaite_core_installed(self):
        qi = get_installer(self.portal)
        self.assertTrue(qi.is_product_installed("senaite.core"))

    def test_content_structure_exists(self):
        existing = self.portal.objectIds()
        self.assertTrue("clients" in existing)
        self.assertTrue("methods" in existing)
        self.assertTrue("samples" in existing)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite
