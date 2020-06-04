# -*- coding: utf-8 -*-

from senaite.core.tests.base import BaseTestCase
from Products.CMFPlone.utils import get_installer


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
        self.assertTrue("analysisrequests" in existing)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite
