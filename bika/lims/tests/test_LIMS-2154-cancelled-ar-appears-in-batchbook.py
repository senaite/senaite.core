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
            self.portal.clients,
            'Client', title='Happy Hills', ClientID='HH')
        contact = self.addthing(
            self.client,
            'Contact', Firstname='Rita', Lastname='Mohale')
        container = self.addthing(
            self.portal.bika_setup.bika_containers,
            'Container', title='Bottle', capacity="10 ml")
        sampletype = self.addthing(
            self.portal.bika_setup.bika_sampletypes,
            'SampleType', title='Water', Prefix='H2O')
        service = self.addthing(
            self.portal.bika_setup.bika_analysisservices,
            'AnalysisService', title='Ecoli', Keyword='ECO', Accredited=True,
            Price='409')
        # Create Sample with single partition
        sample = self.addthing(
            self.client,
            'Sample', SampleType=sampletype)
        self.addthing(sample, 'SamplePartition', Container=container)
        # create a batch
        self.batch = self.addthing(self.portal.clients['client-1'], 'Batch')
        # Create AnalysisRequests
        self.ar1 = self.addthing(
            self.client, 'AnalysisRequest', Contact=contact, Sample=sample,
            Analyses=[service,], SamplingDate=DateTime(), Batch=self.batch)
        self.ar2 = self.addthing(
            self.client, 'AnalysisRequest', Contact=contact, Sample=sample,
            Analyses=[service,], SamplingDate=DateTime(), Batch=self.batch)
        # Cancel one of them
        wf = self.portal.portal_workflow
        wf.doActionFor(self.ar1, 'cancel')
        self.ar1.reindexObject(idxs=['cancellation_state'])
        transaction.commit()

    def tearDown(self):
        super(Test_ShowPrices, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_cancelled_ar_does_not_appear_in_batchbook(self):
        url = self.batch.absolute_url() + "/batchbook"
        browser = self.getBrowser()
        browser.open(url)
        if "H2O-0001-R01" in browser.contents:
            self.fail("H2O-0001-R01 was cancelled, but still appears in "
                      "batchbook.")
        if "H2O-0001-R02" not in browser.contents:
            self.fail("H2O-0001-R02 is active, however does not appear in "
                      "batchbook.")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_ShowPrices))
    suite.layer = BIKA_SIMPLE_FIXTURE
    return suite
