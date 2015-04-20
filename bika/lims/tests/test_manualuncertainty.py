from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils.analysisrequest import create_analysisrequest
from bika.lims.workflow import doActionFor
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
import unittest

try:
    import unittest2 as unittest
except ImportError: # Python 2.7
    import unittest


class TestManualUncertainty(BikaFunctionalTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestManualUncertainty, self).setUp()
        login(self.portal, TEST_USER_NAME)
        servs = self.portal.bika_setup.bika_analysisservices
        # analysis-service-3: Calcium (Ca)
        # analysis-service-6: Cooper (Cu)
        # analysis-service-7: Iron (Fe)
        self.services = [servs['analysisservice-3'],
                         servs['analysisservice-6'],
                         servs['analysisservice-7']]
        for s in self.services:
            s.setAllowManualUncertainty(True)
        uncs = [{'intercept_min': 0, 'intercept_max': 5, 'errorvalue': 0.0015},
                {'intercept_min': 5, 'intercept_max':10, 'errorvalue': 0.02},
                {'intercept_min':10, 'intercept_max':20, 'errorvalue': 0.4}]
        self.services[1].setUncertainties(uncs);
        self.services[2].setUncertainties(uncs);
        self.services[2].setPrecisionFromUncertainty(True)

    def tearDown(self):
        for s in self.services:
            s.setAllowManualUncertainty(False)
            s.setUncertainties([])
            s.setPrecisionFromUncertainty(False)
        logout()
        super(TestManualUncertainty, self).tearDown()

    def test_set_manualuncertainty_field(self):
        for s in self.services:
            self.assertEqual(s.getAllowManualUncertainty(), True)
            self.assertEqual(s.Schema().getField('AllowManualUncertainty').get(s), True)
            s.setAllowManualUncertainty(False)
            self.assertEqual(s.getAllowManualUncertainty(), False)
            self.assertEqual(s.Schema().getField('AllowManualUncertainty').get(s), False)
            s.Schema().getField('AllowManualUncertainty').set(s, True)
            self.assertEqual(s.getAllowManualUncertainty(), True)
            self.assertEqual(s.Schema().getField('AllowManualUncertainty').get(s), True)
            s.Schema().getField('AllowManualUncertainty').set(s, False)
            self.assertEqual(s.getAllowManualUncertainty(), False)
            self.assertEqual(s.Schema().getField('AllowManualUncertainty').get(s), False)
            s.setAllowManualUncertainty(True)

    def test_ar_manageresults_manualuncertainty(self):
        # Input results
        # Client:       Happy Hills
        # SampleType:   Apple Pulp
        # Contact:      Rita Mohale
        # Analyses:     [Calcium, Copper]
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        request = {}
        services = [s.UID() for s in self.services]
        ar = create_analysisrequest(client, request, values, services)

        # Basic uncertainty input
        for a in ar.getAnalyses():
            an = a.getObject()
            self.assertFalse(an.getUncertainty())
            an.setUncertainty('0.2')
            self.assertEqual(an.getUncertainty(), 0.2)
            an.setUncertainty('0.4')
            self.assertEqual(an.getUncertainty(), 0.4)
            an.setUncertainty(None)
            self.assertFalse(an.getUncertainty())

        # Copper (advanced uncertainty)
        cu = [a.getObject() for a in ar.getAnalyses() \
              if a.getObject().getServiceUID() == self.services[1].UID()][0]
        self.assertFalse(cu.getUncertainty())

        # Uncertainty range 5 - 10 (0.2)
        cu.setResult('5.5')
        self.assertEqual(cu.getResult(), '5.5')
        self.assertEqual(cu.getUncertainty(), 0.02)
        cu.setUncertainty('0.8')
        self.assertEqual(cu.getUncertainty(), 0.8)
        cu.setUncertainty(None)
        self.assertEqual(cu.getUncertainty(), 0.02)

        # Uncertainty range 10 - 20 (0.4)
        cu.setResult('15.5')
        self.assertEqual(cu.getResult(), '15.5')
        self.assertEqual(cu.getUncertainty(), 0.4)
        cu.setUncertainty('0.7')
        self.assertEqual(cu.getUncertainty(), 0.7)
        cu.setUncertainty(None)
        self.assertEqual(cu.getUncertainty(), 0.4)

        # Uncertainty range >20 (None)
        cu.setResult('25.5')
        self.assertEqual(cu.getResult(), '25.5')
        self.assertFalse(cu.getUncertainty())
        cu.setUncertainty('0.9')
        self.assertEqual(cu.getUncertainty(), 0.9)
        cu.setUncertainty(None)
        self.assertFalse(cu.getUncertainty())

        # Iron (advanced uncertainty with precision)
        fe = [a.getObject() for a in ar.getAnalyses() \
              if a.getObject().getServiceUID() == self.services[2].UID()][0]
        self.assertFalse(cu.getUncertainty())

        # Uncertainty range 0 - 5 (0.0015)
        fe.setResult('2.3452')
        self.assertEqual(fe.getUncertainty(), 0.0015)
        self.assertEqual(fe.getResult(), '2.3452')
        self.assertEqual(fe.getFormattedResult(), '2.345')
        fe.setUncertainty('0.06')
        self.assertEqual(fe.getUncertainty(), 0.06)
        self.assertEqual(fe.getResult(), '2.3452')
        self.assertEqual(fe.getFormattedResult(), '2.35')
        fe.setUncertainty('0.7')
        self.assertEqual(fe.getUncertainty(), 0.7)
        self.assertEqual(fe.getResult(), '2.3452')
        self.assertEqual(fe.getFormattedResult(), '2.3')
        fe.setUncertainty(None)
        self.assertEqual(fe.getUncertainty(), 0.0015)
        self.assertEqual(fe.getResult(), '2.3452')
        self.assertEqual(fe.getFormattedResult(), '2.345')

        # Uncertainty range 5 - 10 (0.02)
        fe.setResult('8.23462')
        self.assertEqual(fe.getUncertainty(), 0.02)
        self.assertEqual(fe.getResult(), '8.23462')
        self.assertEqual(fe.getFormattedResult(), '8.23')
        fe.setUncertainty('0.6')
        self.assertEqual(fe.getUncertainty(), 0.6)
        self.assertEqual(fe.getResult(), '8.23462')
        self.assertEqual(fe.getFormattedResult(), '8.2')
        fe.setUncertainty('0.07')
        self.assertEqual(fe.getUncertainty(), 0.07)
        self.assertEqual(fe.getResult(), '8.23462')
        self.assertEqual(fe.getFormattedResult(), '8.23')
        fe.setUncertainty(None)
        self.assertEqual(fe.getUncertainty(), 0.02)
        self.assertEqual(fe.getResult(), '8.23462')
        self.assertEqual(fe.getFormattedResult(), '8.23')

        # Uncertainty range >20 (None)
        fe.setResult('25.523345')
        self.assertFalse(fe.getUncertainty())
        self.assertEqual(fe.getResult(), '25.523345')
        self.assertEqual(fe.getPrecision(), 2)
        self.assertEqual(fe.getService().getPrecision(), 2)
        self.assertEqual(fe.getFormattedResult(), '25.52')
        fe.setUncertainty('0.9')
        self.assertEqual(fe.getUncertainty(), 0.9)
        self.assertEqual(fe.getResult(), '25.523345')
        self.assertEqual(fe.getPrecision(), 1)
        self.assertEqual(fe.getService().getPrecision(), 2)
        self.assertEqual(fe.getFormattedResult(), '25.5')
        fe.setUncertainty(None)
        self.assertFalse(fe.getUncertainty())
        self.assertEqual(fe.getResult(), '25.523345')
        self.assertEqual(fe.getPrecision(), 2)
        self.assertEqual(fe.getService().getPrecision(), 2)
        self.assertEqual(fe.getFormattedResult(), '25.52')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestManualUncertainty))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
