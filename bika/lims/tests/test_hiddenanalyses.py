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


class TestHiddenAnalyses(BikaFunctionalTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestHiddenAnalyses, self).setUp()
        login(self.portal, TEST_USER_NAME)
        servs = self.portal.bika_setup.bika_analysisservices

        # analysis-service-3: Calcium (Ca)
        # analysis-service-6: Cooper (Cu)
        # analysis-service-7: Iron (Fe)
        self.services = [servs['analysisservice-3'],
                         servs['analysisservice-6'],
                         servs['analysisservice-7']]

        # Calcium - Hidden not set
        # Copper  - Hidden set to False
        self.services[1].setHidden(False)
        # Iron    - Hidden set to True
        self.services[2].setHidden(True)

        profs = self.portal.bika_setup.bika_analysisprofiles
        # analysisprofile-1: Trace Metals
        self.analysisprofile = profs['analysisprofile-1']

        artemp = self.portal.bika_setup.bika_artemplates
        # artemplate-2: Bruma Metals
        self.artemplate = artemp['artemplate-2']

    def tearDown(self):
        # Restore
        for s in self.services:
            s.setHidden(False)

        self.analysisprofile.setAnalysisServicesSettings([])
        self.artemplate.setAnalysisServicesSettings([])

        logout()
        super(TestHiddenAnalyses, self).tearDown()

    def test_service_hidden_service(self):
        service = self.services[1]
        uid = service.UID()
        self.assertFalse(service.getHidden())
        self.assertFalse(service.Schema().getField('Hidden').get(service))

        service.setHidden(False)
        self.assertFalse(service.getHidden())
        self.assertFalse(service.Schema().getField('Hidden').get(service))
        service.setHidden(True)
        self.assertTrue(service.getHidden())
        self.assertTrue(service.Schema().getField('Hidden').get(service))

        # Restore
        service.setHidden(False)

    def test_service_hidden_profile(self):
        # Profile
        # For Calcium (unset)
        uid = self.services[0].UID();
        self.assertFalse(self.services[0].getHidden())
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))

        # For Copper (False)
        uid = self.services[1].UID()
        self.assertFalse(self.services[1].getHidden())
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))

        # For Iron (True)
        uid = self.services[2].UID()
        self.assertTrue(self.services[2].getHidden())
        self.assertTrue(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))

        # Modify visibility for Calcium in profile
        uid = self.services[0].UID();
        sets = [{'uid': uid}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': False}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))

        sets = [{'uid': uid, 'hidden': True}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertTrue(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))

        # Modify visibility for Cooper in profile
        uid = self.services[1].UID();
        sets = [{'uid': uid}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': False}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': True}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertTrue(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))

        # Modify visibility for Iron in profile
        uid = self.services[2].UID();
        sets = [{'uid': uid}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertTrue(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': False}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': True}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertTrue(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))

        # Restore
        self.analysisprofile.setAnalysisServicesSettings([])

    def test_service_hidden_artemplate(self):
        # Template
        # For Calcium (unset)
        uid = self.services[0].UID();
        self.assertFalse(self.services[0].getHidden())
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.artemplate.getAnalysisServiceSettings(uid))

        # For Copper (False)
        uid = self.services[1].UID()
        self.assertFalse(self.services[1].getHidden())
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.artemplate.getAnalysisServiceSettings(uid))

        # For Iron (True)
        uid = self.services[2].UID()
        self.assertTrue(self.services[2].getHidden())
        self.assertTrue(self.artemplate.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.artemplate.getAnalysisServiceSettings(uid))

        # Modify visibility for Calcium in template
        uid = self.services[0].UID();
        sets = [{'uid': uid}]
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.artemplate.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': False}]
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.artemplate.getAnalysisServiceSettings(uid))

        sets = [{'uid': uid, 'hidden': True}]
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertTrue(self.artemplate.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.artemplate.getAnalysisServiceSettings(uid))

        # Modify visibility for Cooper in template
        uid = self.services[1].UID();
        sets = [{'uid': uid}]
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.artemplate.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': False}]
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.artemplate.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': True}]
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertTrue(self.artemplate.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.artemplate.getAnalysisServiceSettings(uid))

        # Modify visibility for Iron in template
        uid = self.services[2].UID();
        sets = [{'uid': uid}]
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertTrue(self.artemplate.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.artemplate.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': False}]
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.artemplate.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': True}]
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertTrue(self.artemplate.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in self.artemplate.getAnalysisServiceSettings(uid))

        # Restore
        self.artemplate.setAnalysisServicesSettings([])

    def test_service_hidden_analysisrequest(self):
        # Input results
        # Client:       Happy Hills
        # SampleType:   Apple Pulp
        # Contact:      Rita Mohale
        # Analyses:     [Calcium, Copper, Iron]
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        request = {}
        services = [s.UID() for s in self.services]
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        ar = create_analysisrequest(client, request, values, services)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(services[0]))
        self.assertFalse(ar.isAnalysisServiceHidden(services[0]))
        self.assertFalse(ar.getAnalysisServiceSettings(services[1]).get('hidden'))
        self.assertFalse(ar.isAnalysisServiceHidden(services[1]))
        self.assertFalse(ar.getAnalysisServiceSettings(services[2]).get('hidden'))
        self.assertTrue(ar.isAnalysisServiceHidden(services[2]))

        # For Calcium (unset)
        uid = self.services[0].UID()
        self.assertFalse(self.services[0].getHidden())
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in self.artemplate.getAnalysisServiceSettings(uid))

        # For Copper (False)
        uid = self.services[1].UID()
        self.assertFalse(self.services[1].getHidden())
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))

        # For Iron (True)
        uid = self.services[2].UID()
        self.assertTrue(self.services[2].getHidden())
        self.assertTrue(ar.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))

        # Modify visibility for Calcium in AR
        uid = self.services[0].UID();
        sets = [{'uid': uid}]
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': False}]
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in ar.getAnalysisServiceSettings(uid))
        sets = [{'uid': uid, 'hidden': True}]
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.isAnalysisServiceHidden(uid))
        self.assertTrue('hidden' in ar.getAnalysisServiceSettings(uid))
        ar.setAnalysisServicesSettings([])

        # AR with profile with no changes
        values['Profile'] = self.analysisprofile.UID()
        ar = create_analysisrequest(client, request, values, services)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(services[0]))
        self.assertFalse(ar.getAnalysisServiceSettings(services[1]).get('hidden'))
        self.assertFalse(ar.getAnalysisServiceSettings(services[2]).get('hidden'))
        uid = self.services[0].UID()
        self.assertFalse(self.services[0].getHidden())
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        uid = self.services[1].UID()
        self.assertFalse(self.services[1].getHidden())
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        uid = self.services[2].UID()
        self.assertTrue(self.services[2].getHidden())
        self.assertTrue(ar.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))

        # AR with template with no changes
        values['Template'] = self.artemplate
        del values['Profile']
        ar = create_analysisrequest(client, request, values, services)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(services[0]))
        self.assertFalse(ar.getAnalysisServiceSettings(services[1]).get('hidden'))
        self.assertFalse(ar.getAnalysisServiceSettings(services[2]).get('hidden'))
        uid = self.services[0].UID()
        self.assertFalse(self.services[0].getHidden())
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        uid = self.services[1].UID()
        self.assertFalse(self.services[1].getHidden())
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        uid = self.services[2].UID()
        self.assertTrue(self.services[2].getHidden())
        self.assertTrue(ar.isAnalysisServiceHidden(uid))
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))

        # AR with profile, with changes
        values['Profile'] = self.analysisprofile.UID()
        del values['Template']
        matrix = [[2, 1,-2],  # AS = Not set
                  [2, 1,-2],  # AS = False
                  [2, 1,-1]]
        for i in range(len(matrix)):
            sets = {'uid': services[i]}
            opts = [0, 1, 2]
            for j in opts:
                if j == 0:
                    sets['hidden'] = False
                elif j == 1:
                    sets['hidden'] = True
                else:
                    del sets['hidden']
                self.analysisprofile.setAnalysisServicesSettings(sets)
                ar = create_analysisrequest(client, request, values, services)
                res = matrix[i][j]
                if res < 0:
                    self.assertFalse('hidden' in ar.getAnalysisServiceSettings(services[i]))
                else:
                    self.assertTrue('hidden' in ar.getAnalysisServiceSettings(services[i]))
                if abs(res) == 1:
                    self.assertTrue(ar.isAnalysisServiceHidden(services[i]))
                elif abs(res) == 2:
                    self.assertFalse(ar.isAnalysisServiceHidden(services[i]))

        # Restore
        self.analysisprofile.setAnalysisServicesSettings([])

        # AR with template, with changes
        values['Template'] = self.artemplate.UID()
        del values['Profile']
        matrix = [[2, 1,-2],  # AS = Not set
                  [2, 1,-2],  # AS = False
                  [2, 1,-1]]
        for i in range(len(matrix)):
            sets = {'uid': services[i]}
            opts = [0, 1, 2]
            for j in opts:
                if j == 0:
                    sets['hidden'] = False
                elif j == 1:
                    sets['hidden'] = True
                else:
                    del sets['hidden']
                self.artemplate.setAnalysisServicesSettings(sets)
                ar = create_analysisrequest(client, request, values, services)
                res = matrix[i][j]
                if res < 0:
                    self.assertFalse('hidden' in ar.getAnalysisServiceSettings(services[i]))
                else:
                    self.assertTrue('hidden' in ar.getAnalysisServiceSettings(services[i]))
                if abs(res) == 1:
                    self.assertTrue(ar.isAnalysisServiceHidden(services[i]))
                elif abs(res) == 2:
                    self.assertFalse(ar.isAnalysisServiceHidden(services[i]))

        # Restore
        self.artemplate.setAnalysisServicesSettings([])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHiddenAnalyses))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
