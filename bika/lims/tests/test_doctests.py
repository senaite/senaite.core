from Products.PloneTestCase import PloneTestCase
from Products.validation import validation
from Testing import ZopeTestCase as ztc
from bika.lims import content,browser
from bika.lims.testing import BIKA_LIMS_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from plone.app.testing import *
from plone.testing import z2
import doctest
import json
import unittest

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(ztc.ZopeDocTestSuite(module="bika.lims.browser.sample", test_class=unittest.TestCase))
    suite.addTests(ztc.ZopeDocTestSuite(module="bika.lims.content.analysisservice", test_class=unittest.TestCase))
    suite.addTests(ztc.ZopeDocTestSuite(module="bika.lims.controlpanel.bika_analysisservices", test_class=unittest.TestCase))
    suite.layer = BIKA_LIMS_FUNCTIONAL_TESTING
    return suite
