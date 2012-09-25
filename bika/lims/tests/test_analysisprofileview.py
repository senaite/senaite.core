from Products.CMFCore.utils import getToolByName
from Products.Five.testbrowser import Browser
from Products.validation import validation
from bika.lims.testing import BIKA_LIMS_FUNCTIONAL_TESTING
from Products.Archetypes.config import REFERENCE_CATALOG
from bika.lims.tests.base import *
from plone.app.testing import *
from plone.testing import z2
import unittest

class Tests(BikaFunctionalTestCase):

    baseurl = None
    browser = None

    def setUp(self):
        BikaFunctionalTestCase.setUp(self)
        login(self.portal, TEST_USER_NAME)
        self.browser = self.browserLogin()
        self.baseurl = self.browser.url
        self.bsc = getToolByName(self.portal, 'bika_setup_catalog')

    def test_setup_supplied_values(self):
        self.browser.open("%s%s" % (self.baseurl, "/bika_setup/bika_analysisprofiles/analysisprofile-1"))
        self.assertTrue(u"Trace Metals" in self.browser.contents)
        control = self.browser.getControl(name="uids:list")
        uids = control.value
        all_uids = control.options
        self.assertEqual(len(uids), 7)
        self.assertTrue(len(all_uids) > 7)

        # select all and save
        control.value = all_uids
        self.browser.getControl(name='form.button.save').click()
        self.browser.open("%s%s" % (self.baseurl, "/bika_setup/bika_analysisprofiles/analysisprofile-1"))
        self.assertEqual(control.value,
                         all_uids)

        # revert and save
        control = self.browser.getControl(name="uids:list")
        control.value = uids
        self.browser.getControl(name='form.button.save').click()
        self.browser.open("%s%s" % (self.baseurl, "/bika_setup/bika_analysisprofiles/analysisprofile-1"))
        self.assertEqual(control.value,
                         uids)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_LIMS_FUNCTIONAL_TESTING
    return suite
