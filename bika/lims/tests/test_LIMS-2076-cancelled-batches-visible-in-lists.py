"""If ShowPrices is not true, then Invoices, prices, pricelists, should
all be hidden.
"""
from bika.lims.testing import BIKA_SIMPLE_FIXTURE
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils import tmpID
from DateTime.DateTime import DateTime
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

import transaction
import unittest

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


class Test_ShowPrices(BikaFunctionalTestCase):
    def addthing(self, folder, portal_type, **kwargs):
        thing = _createObjectByType(portal_type, folder, tmpID())
        thing.unmarkCreationFlag()
        thing.edit(**kwargs)
        thing._renameAfterCreation()
        return thing

    def setUp(self):
        super(Test_ShowPrices, self).setUp()
        login(self.portal, TEST_USER_NAME)
        self.client = self.addthing(
            self.portal.clients, 'Client', title='Happy Hills', ClientID='HH')
        # create some batches
        batch1 = self.addthing(self.portal.clients['client-1'], 'Batch')
        batch2 = self.addthing(self.portal.clients['client-1'], 'Batch')
        batch3 = self.addthing(self.portal.batches, 'Batch')
        batch4 = self.addthing(self.portal.batches, 'Batch')
        # Cancel one of them
        wf = self.portal.portal_workflow
        wf.doActionFor(batch1, 'cancel')
        wf.doActionFor(batch3, 'cancel')
        batch1.reindexObject(idxs=['cancellation_state'])
        batch3.reindexObject(idxs=['cancellation_state'])
        transaction.commit()

    def tearDown(self):
        super(Test_ShowPrices, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_default_root_view_does_not_show_cancelled_items(self):
        url = self.portal.batches.absolute_url()
        browser = self.getBrowser()
        browser.open(url)
        if "B-001" in browser.contents:
            self.fail("B-001 was cancelled, but still appears in  "
                      "ROOT default batch listing")
        if "B-003" in browser.contents:
            self.fail("B-003 was cancelled, but still appears in  "
                      "ROOT default batch listing")
        if "B-002" not in browser.contents:
            self.fail("B-002 is active, however it does not appear "
                      "ROOT default batch listing")
        if "B-004" not in browser.contents:
            self.fail("B-004 is active, however it does not appear "
                      "ROOT default batch listing")

    def test_cancelled_root_view_shows_only_cancelled_items(self):
        url = self.portal.batches.absolute_url() + \
              "?list_review_state=cancelled"
        browser = self.getBrowser()
        browser.open(url)
        if "B-001" not in browser.contents:
            self.fail("B-001 was cancelled, but does not appear in "
                      "ROOT cancelled batch listing")
        if "B-003" not in browser.contents:
            self.fail("B-003 was cancelled, but does not appear in "
                      "ROOT cancelled batch listing")
        if "B-002" in browser.contents:
            self.fail("b-002 is active, however it appears in "
                      "ROOT cancelled batch listing")
        if "B-004" in browser.contents:
            self.fail("b-004 is active, however it appears in "
                      "ROOT cancelled batch listing")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_ShowPrices))
    suite.layer = BIKA_SIMPLE_FIXTURE
    return suite
