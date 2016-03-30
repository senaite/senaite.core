# -*- coding: utf-8 -*-

from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils.analysisrequest import create_analysisrequest
from bika.lims.workflow import doActionFor
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
import unittest

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class Test_LIMS2001(BikaFunctionalTestCase):
    """
    When adding a duplicate for an AR in a worksheet, only the first analysis
    gets duplicated: https://jira.bikalabs.com/browse/LIMS-2001
    """
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(Test_LIMS2001, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def tearDown(self):
        logout()
        super(Test_LIMS2001, self).tearDown()

    def test_LIMS2001(self):
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_LIMS2001))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
