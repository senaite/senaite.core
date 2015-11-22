"""If ShowPrices is not true, then Invoices, prices, pricelists, should
all be hidden.
"""
from bika.lims.testing import BIKA_SIMPLE_FIXTURE
from bika.lims.tests.base import BikaSimpleTestCase
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


class Test_ShowPrices(BikaSimpleTestCase):

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
        self.client = self.addthing(
            self.portal.clients,
            'Client', title='Happy Hills', ClientID='HH')
        contact = self.addthing(
            self.client,
            'Contact', Firstname='Rita', Lastname='Mohale')
        container = self.addthing(
            self.portal.bika_setup.bika_containers,
            'Container', title='Bottle', capacity="10ml")
        sampletype = self.addthing(
            self.portal.bika_setup.bika_sampletypes,
            'SampleType', title='Water', Prefix='H2O')
        service = self.addthing(
            self.portal.bika_setup.bika_analysisservices,
            'AnalysisService', title='Ecoli', Keyword='ECO', Accredited=True,
            Price='409')
        self.profile = self.addthing(
            self.portal.bika_setup.bika_analysisprofiles,
            'AnalysisProfile', title='Profile', Service=[service,])
        self.template = self.addthing(
            self.portal.bika_setup.bika_artemplates,
            'ARTemplate', title='Template',
            Analyses=[{'partition': 'part-1', 'service_uid': service.UID()}])
        # Create Sample with single partition
        sample = self.addthing(
            self.client,
            'Sample', SampleType=sampletype)
        part = self.addthing(
            sample,
            'SamplePartition', Container=container)
        # Create AnalysisService with single service
        self.ar = self.addthing(
            self.client,
            'AnalysisRequest', Contact=contact, Sample=sample,
            Analyses=[service,], SamplingDate=DateTime())
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

    def test_ar_add_by_cols(self):
        url = self.portal.clients['client-1'].absolute_url() + \
              "/portal_factory/AnalysisRequest/x/ar_add?layout=columns"
        browser = self.getBrowser()
        self.portal.bika_setup.setShowPrices(True)
        transaction.commit()
        browser.open(url)
        if browser.contents.find('subtotal') == -1:
            self.fail('ShowPrices is True, but the AR-Add columns form '
                      'does not contain price rows')
        if browser.contents.find('Exclude') == -1:
            self.fail('ShowPrices is True, but the AR-Add columns form '
                      'does not contain Invoice Exclude field')
        self.portal.bika_setup.setShowPrices(False)
        transaction.commit()
        browser.open(url)
        if browser.contents.find('subtotal') > -1:
            self.fail('ShowPrices is False, but the AR-Add columns form '
                      'still contains price rows')
        if browser.contents.find('Exclude') > -1:
            self.fail('ShowPrices is True, but the AR-Add columns form still'
                      'shows the Invoice Exclude field')

    def test_accreditation_page(self):
        url = self.portal.absolute_url() + "/accreditation"
        browser = self.getBrowser()
        self.portal.bika_setup.setShowPrices(True)
        transaction.commit()
        browser.open(url)
        if browser.contents.find('409') == -1:
            self.fail('ShowPrices is True, but the accreditation screen does '
                      'not contain price column')
        self.portal.bika_setup.setShowPrices(False)
        transaction.commit()
        browser.open(url)
        if browser.contents.find('409') > -1:
            self.fail('ShowPrices is False, but the accreditation screen still '
                      'includes price column')

    def test_analysisprofile_analyses_list(self):
        url = self.profile.absolute_url()
        browser = self.getBrowser()
        self.portal.bika_setup.setShowPrices(True)
        transaction.commit()
        browser.open(url)
        if browser.contents.find('409') == -1:
            self.fail('ShowPrices is True, but profile analyses widget does '
                      'not contain price column')
        self.portal.bika_setup.setShowPrices(False)
        transaction.commit()
        browser.open(url)
        if browser.contents.find('409') > -1:
            self.fail('ShowPrices is False, but profile analyses widget still '
                      'includes price column')

    def test_artemplate_analyses_list(self):
        url = self.template.absolute_url()
        browser = self.getBrowser()
        self.portal.bika_setup.setShowPrices(True)
        transaction.commit()
        browser.open(url)
        if browser.contents.find('409') == -1:
            self.fail('ShowPrices is True, but AR Template analyses widget '
                      'does not contain price column')
        self.portal.bika_setup.setShowPrices(False)
        transaction.commit()
        browser.open(url)
        if browser.contents.find('409') > -1:
            self.fail('ShowPrices is False, but AR Template analyses widget '
                      'still includes price column')

    def test_client_discount_fields(self):
        url = self.portal.clients['client-1'].absolute_url() + "/edit"
        browser = self.getBrowser()
        self.portal.bika_setup.setShowPrices(True)
        transaction.commit()
        browser.open(url)
        if browser.contents.find('discount') == -1:
            self.fail('ShowPrices is True, but Client edit page does not '
                      'contain Discount fields')
        self.portal.bika_setup.setShowPrices(False)
        transaction.commit()
        browser.open(url)
        if browser.contents.find('discount') > -1:
            self.fail('ShowPrices is False, but Client edit page still '
                      'contains Discount fields')

    def test_analysisservice_fields(self):
        bs = self.portal.bika_setup
        listing_url = bs.bika_analysisservices.absolute_url()
        service_url = bs.bika_analysisservices.objectValues()[0].absolute_url()
        browser = self.getBrowser()
        self.portal.bika_setup.setShowPrices(True)
        transaction.commit()
        browser.open(listing_url)
        if browser.contents.find('409') == -1:
            self.fail('ShowPrices is True, but Service listing view does not '
                      'contain Price fields')
        self.portal.bika_setup.setShowPrices(False)
        transaction.commit()
        browser.open(listing_url)
        if browser.contents.find('409') > -1:
            self.fail('ShowPrices is False, but Service listing view still '
                      'contains Price fields')
        browser.open(service_url)
        if browser.contents.find('Price') == -1:
            self.fail('Service edit form must always contain Price field, even '
                      ' when ShowPrices is disabled.')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_ShowPrices))
    suite.layer = BIKA_SIMPLE_FIXTURE
    return suite
