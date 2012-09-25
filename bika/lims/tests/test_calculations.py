from Products.validation import validation
from bika.lims.browser.calcs import ajaxCalculateAnalysisEntry
from bika.lims.testing import BIKA_LIMS_INTEGRATION_TESTING
from bika.lims.tests.base import BikaIntegrationTestCase
from plone.app.testing import *
from plone.testing import z2
import json
import unittest

class Tests(BikaIntegrationTestCase):
    pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_LIMS_INTEGRATION_TESTING
    return suite
