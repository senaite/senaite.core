from Products.validation import validation
from bika.lims.browser.calcs import ajaxCalculateAnalysisEntry
from bika.lims.testing import BIKA_LIMS_INTEGRATION_TESTING
from bika.lims.tests.base import BikaIntegrationTestCase
from plone.app.testing import *
from plone.testing import z2
import json
import unittest

class Tests(BikaIntegrationTestCase):

    """These tests are from testTranslationServiceTool.py, but with
    different default formats.
    """

    def afterSetUp(self):
        self.tool = getToolByName(self.portal, 'translation_service')

    def ulocalized_time(time, long_format=None), time_only=False, context=None):
        return self.tool.ulocalized_time(
            time, long_format, time_only, context, 'bika')

    def testLocalized_time(self):
        value = self.ulocalized_time('9 Mar, 1997 1:45pm',
                                         long_format=True,
                                         time_only=False,
                                         context=self.portal)
        # TranslationServiceTool falls back to time formats in site properties
        # because PTS isn't installed
        # bika has not modified these values.
        self.assertEquals(value, 'Mar 09, 1997 01:45 PM')

    def testLocalized_time_only_none(self):
        value = self.ulocalized_time('9 Mar, 1997 1:45pm',
                                         long_format=True,
                                         time_only=None,
                                         context=self.portal)
        # TranslationServiceTool falls back to time formats in site properties
        # because PTS isn't installed
        # bika has not modified these values.
        self.assertEquals(value, 'Mar 09, 1997 01:45 PM')

    def testLocalized_time_only(self):
        value = self.ulocalized_time('Mar 9, 1997 1:45pm',
                                         long_format=False,
                                         time_only=True,
                                         context=self.portal)
        # TranslationServiceTool falls back to time formats in site properties
        # because PTS isn't installed
        # bika has not modified these values.
        self.assertEquals(value, '01:45 PM')

    def test_ulocalized_time_fetch_error(self):
        # http://dev.plone.org/plone/ticket/4251
        error = "(Missing.Value,), {}"
        value = self.ulocalized_time(error)
        self.assertEqual(value, None)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_LIMS_INTEGRATION_TESTING
    return suite
