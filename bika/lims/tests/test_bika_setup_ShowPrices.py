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
    layer = BIKA_SIMPLE_FIXTURE

    def addthing(self, folder, portal_type, **kwargs):
        thing = _createObjectByType(portal_type, folder, tmpID())
        thing.unmarkCreationFlag()
        thing.edit(**kwargs)
        thing._renameAfterCreation()
        return thing

    def setUp(self):
        # @formatter:off
        super(Test_ShowPrices, self).setUp()
        login(self.portal, TEST_USER_NAME)
        self.client = self.addthing(self.portal.clients, 'Client', title='Happy Hills', ClientID='HH')
        contact = self.addthing(self.client, 'Contact', Firstname='Rita', Lastname='Mohale')
        container = self.addthing(self.portal.bika_setup.bika_containers, 'Container', title='Bottle', capacity="10ml")
        sampletype = self.addthing(self.portal.bika_setup.bika_sampletypes, 'SampleType', title='Water', Prefix='H2O')
        service = self.addthing(self.portal.bika_setup.bika_analysisservices, 'AnalysisService', title='Ecoli', Keyword='ECO')
        # Create Sample with single partition
        sample = self.addthing(self.client, 'Sample', SampleType=sampletype)
        part = self.addthing(sample, 'SamplePartition', Container=container)
        # Create AnalysisService with single service
        self.ar = self.addthing(self.client, 'AnalysisRequest', Contact=contact, Sample=sample, Analyses=[service,], SamplingDate=DateTime())
        # @formatter:on
        transaction.commit()

    def tearDown(self):
        super(Test_ShowPrices, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_analysisrequest_view(self):
        browser = self.getBrowser()
        self.portal.bika_setup.setShowPrices(True)
        transaction.commit()
        browser.open(self.ar.absolute_url())
        if browser.contents.find('contentview-invoice') == -1:
            self.fail('ShowPrices is True, but the Invoice tab does not appear '
                      'in an AnalysisRequest view page!')
        self.portal.bika_setup.setShowPrices(False)
        transaction.commit()
        browser.open(self.ar.absolute_url())
        if browser.contents.find('contentview-invoice') > -1:
            self.fail('ShowPrices is False, but the Invoice tab does appear '
                      'in an AnalysisRequest view page!')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_ShowPrices))
    suite.layer = BIKA_SIMPLE_FIXTURE
    return suite
