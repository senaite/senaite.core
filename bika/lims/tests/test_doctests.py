from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from doctest import DocFileSuite
from doctest import DocTestSuite
from plone.testing import layered
import doctest
import unittest

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([

        layered(DocTestSuite(module='bika.lims.vocabularies',
                             optionflags=OPTIONFLAGS),
                layer=BIKA_FUNCTIONAL_TESTING),


    ])
    return suite

    # suite.addTests(ztc.ZopeDocTestSuite(module="", test_class=unittest.TestCase))
    # # suite.addTests(ztc.ZopeDocTestSuite(module="bika.lims.browser.sample", test_class=unittest.TestCase))
    # # suite.addTests(ztc.ZopeDocTestSuite(module="bika.lims.content.analysisservice", test_class=unittest.TestCase))
    # # suite.addTests(ztc.ZopeDocTestSuite(module="bika.lims.controlpanel.bika_analysisservices", test_class=unittest.TestCase))
    # suite.layer = BIKA_FUNCTIONAL_TESTING
    # return suite
