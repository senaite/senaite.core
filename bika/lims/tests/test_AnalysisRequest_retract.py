from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName
from bika.lims.utils import tmpID
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.idserver import renameAfterCreation
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from datetime import date
from bika.lims.utils.analysisrequest import create_analysisrequest
import unittest

try:
    import unittest2 as unittest
except ImportError: # Python 2.7
    import unittest


class TestAnalysisRequestRetract(BikaFunctionalTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestAnalysisRequestRetract, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_retract_an_analysis_request(self):
        #Test the retract process to avoid LIMS-1989
        catalog = getToolByName(self.portal, 'portal_catalog')
        # Getting the first client
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        # Getting some services
        services = catalog(portal_type = 'AnalysisService',
                            inactive_state = 'active')[:3]
        service_uids = [service.getObject().UID() for service in services]
        request = {}
        ar = create_analysisrequest(client, request, values, service_uids)
        wf = getToolByName(ar, 'portal_workflow')
        wf.doActionFor(ar, 'receive')

        # Cheking if everything is going OK
        #import pdb; pdb.set_trace()
        self.assertEquals(ar.portal_workflow.getInfoFor(ar, 'review_state'),
                                                        'sample_received')
        for analysis in ar.getAnalyses(full_objects=True):
            analysis.setResult('12')
            wf.doActionFor(analysis, 'submit')
            self.assertEquals(analysis.portal_workflow.getInfoFor(analysis,
                            'review_state'),'to_be_verified')
            # retracting results
            wf.doActionFor(analysis, 'retract')
            self.assertEquals(analysis.portal_workflow.getInfoFor(analysis,
                            'review_state'),'retracted')
        for analysis in ar.getAnalyses(full_objects=True):
            if analysis.portal_workflow.getInfoFor(analysis,
                'review_state') == 'retracted':
                continue
            wf.doActionFor(analysis, 'submit')
            self.assertEquals(analysis.portal_workflow.getInfoFor(analysis,
                            'review_state'),'to_be_verified')
        wf.doActionFor(ar, 'retract')
        self.assertEquals(ar.portal_workflow.getInfoFor(ar, 'review_state'),
                                                        'sample_received')

    def tearDown(self):
        logout()
        super(TestAnalysisRequestRetract, self).tearDown()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAnalysisRequestRetract))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
