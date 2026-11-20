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
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.tests.base import DataTestCase


class TestMethodServiceLink(DataTestCase):
    """The demo data links analysis services to (Dexterity) methods
    """

    def test_methods_are_dexterity_and_in_setup(self):
        methods = self.portal.setup.methods.objectValues()
        self.assertGreater(len(methods), 0)
        for method in methods:
            self.assertEqual(api.get_portal_type(method), "Method")
            self.assertTrue(api.is_dexterity_content(method))

    def test_services_have_methods_assigned(self):
        catalog = api.get_tool(SETUP_CATALOG)
        services = catalog(portal_type="AnalysisService")
        with_methods = [b for b in services if api.get_object(b).getMethods()]
        self.assertGreater(
            len(with_methods), 0,
            "no analysis service has a method assigned")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMethodServiceLink))
    return suite
