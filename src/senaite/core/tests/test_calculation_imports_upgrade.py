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

import unittest

from plone.app.testing import logout
from plone.registry.interfaces import IRegistry
from senaite.core.api.calculation import IMPORT_MODULES_RECORD
from senaite.core.config.registry import CALCULATION_IMPORT_MODULES
from senaite.core.tests.base import DataTestCase
from senaite.core.upgrade.v02_07_000 import allow_calculation_imports
from zope.component import getUtility


class TestAllowCalculationImports(DataTestCase):
    """The upgrade step allows the modules the calculations import from
    """

    def test_module_of_a_calculation_is_allowed(self):
        calculation = self.portal.setup.calculations["calculation-1"]
        # an import as the form stores it, unicode, of a module that is
        # not allowed by default
        calculation.setPythonImports(
            [{"module": u"json", "function": u"dumps"}])
        registry = getUtility(IRegistry)
        registry[IMPORT_MODULES_RECORD] = list(CALCULATION_IMPORT_MODULES)

        # whoever runs the upgrade, the calculation counts
        logout()
        allow_calculation_imports(self.portal.portal_setup)

        modules = registry[IMPORT_MODULES_RECORD]
        self.assertIn("json", modules)
        # the record holds ASCII text
        self.assertTrue(all(isinstance(module, str) for module in modules))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAllowCalculationImports))
    return suite
