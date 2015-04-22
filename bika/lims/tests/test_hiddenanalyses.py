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
        self.services[1].setHidden(False)
        self.services[2].setHidden(False)
        logout()
        super(TestHiddenAnalyses, self).tearDown()

    def test_set_hidden_field(self):
        # analyses
        self.assertFalse(self.services[0].getHidden())
        self.assertFalse(self.services[0].Schema().getField('Hidden').get(self.services[0]))
        self.assertFalse('hidden' in self.analysisprofile.getAnalysisServiceSettings(self.services[0].UID()))
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(self.services[0].UID()))
        self.assertFalse('hidden' in self.artemplate.getAnalysisServiceSettings(self.services[0].UID()))
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(self.services[0].UID()))

        self.assertFalse(self.services[1].getHidden())
        self.assertFalse(self.services[1].Schema().getField('Hidden').get(self.services[1]))
        self.assertFalse(self.analysisprofile.getAnalysisServiceSettings(self.services[1].UID()).get('hidden'))
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(self.services[1].UID()))
        self.assertFalse(self.artemplate.getAnalysisServiceSettings(self.services[1].UID()).get('hidden'))
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(self.services[1].UID()))

        self.assertTrue(self.services[2].getHidden(), True)
        self.assertTrue(self.services[2].Schema().getField('Hidden').get(self.services[2]))
        self.assertTrue(self.analysisprofile.getAnalysisServiceSettings(self.services[2].UID()).get('hidden'))
        self.assertTrue(self.analysisprofile.isAnalysisServiceHidden(self.services[2].UID()))
        self.assertTrue(self.artemplate.getAnalysisServiceSettings(self.services[2].UID()).get('hidden'))
        self.assertTrue(self.artemplate.isAnalysisServiceHidden(self.services[2].UID()))

        self.services[1].setHidden(True)
        self.assertTrue(self.services[1].getHidden(), True)
        self.assertTrue(self.services[1].Schema().getField('Hidden').get(self.services[1]))
        self.assertTrue(self.analysisprofile.getAnalysisServiceSettings(self.services[1].UID()).get('hidden'))
        self.assertTrue(self.analysisprofile.isAnalysisServiceHidden(self.services[1].UID()))
        self.assertTrue(self.artemplate.getAnalysisServiceSettings(self.services[1].UID()).get('hidden'))
        self.assertTrue(self.artemplate.isAnalysisServiceHidden(self.services[1].UID()))

        self.services[2].setHidden(False)
        self.assertFalse(self.services[2].getHidden())
        self.assertFalse(self.services[2].Schema().getField('Hidden').get(self.services[2]))
        self.assertFalse(self.analysisprofile.getAnalysisServiceSettings(self.services[2].UID()).get('hidden'))
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(self.services[2].UID()))
        self.assertFalse(self.artemplate.getAnalysisServiceSettings(self.services[2].UID()).get('hidden'))
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(self.services[2].UID()))

        self.services[1].setHidden(False)
        self.assertFalse(self.services[1].getHidden())
        self.assertFalse(self.services[1].Schema().getField('Hidden').get(self.services[1]))
        self.assertFalse(self.analysisprofile.getAnalysisServiceSettings(self.services[1].UID()).get('hidden'))
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(self.services[1].UID()))
        self.assertFalse(self.artemplate.getAnalysisServiceSettings(self.services[1].UID()).get('hidden'))
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(self.services[1].UID()))

        self.services[2].setHidden(True)
        self.assertTrue(self.services[2].getHidden())
        self.assertTrue(self.services[2].Schema().getField('Hidden').get(self.services[2]))
        self.assertTrue(self.analysisprofile.getAnalysisServiceSettings(self.services[2].UID()).get('hidden'))
        self.assertTrue(self.analysisprofile.isAnalysisServiceHidden(self.services[1].UID()))
        self.assertTrue(self.artemplate.getAnalysisServiceSettings(self.services[2].UID()).get('hidden'))
        self.assertTrue(self.artemplate.isAnalysisServiceHidden(self.services[2].UID()))

        # profile
        uid = self.services[0].UID()
        sets = [{'uid': uid}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        sets[0]['hidden'] = False
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(self.analysisprofile.getAnalysisServiceSettings(uid).get('hidden'))
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        sets[0]['hidden'] = True
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertTrue(self.analysisprofile.getAnalysisServiceSettings(uid).get('hidden'))
        self.assertTrue(self.analysisprofile.isAnalysisServiceHidden(uid))
        sets = []
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in self.analysisprofile.getAnalysisServiceSettings(uid))
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))

        # template
        uid = self.services[0].UID()
        sets = [{'uid': uid}]
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in self.artemplate.getAnalysisServiceSettings(uid))
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(uid))
        sets[0]['hidden'] = False
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(self.artemplate.getAnalysisServiceSettings(uid).get('hidden'))
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(uid))
        sets[0]['hidden'] = True
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertTrue(self.artemplate.getAnalysisServiceSettings(uid).get('hidden'))
        self.assertTrue(self.artemplate.isAnalysisServiceHidden(uid))
        sets = []
        self.artemplate.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in self.artemplate.getAnalysisServiceSettings(uid))
        self.assertFalse(self.artemplate.isAnalysisServiceHidden(uid))

    def test_ar_hidden_analyses(self):
        # Calcium - Hidden not set
        # Copper  - Hidden set to False
        self.services[1].setHidden(False)
        # Iron    - Hidden set to True
        self.services[2].setHidden(True)

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
        self.assertTrue(ar.getAnalysisServiceSettings(services[2]).get('hidden'))
        self.assertTrue(ar.isAnalysisServiceHidden(services[2]))
        uid = services[0]
        sets = [{'uid': uid}]
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        sets[0]['hidden'] = False
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = True
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets = []
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        uid = services[1]
        sets = [{'uid': uid}]
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        sets[0]['hidden'] = False
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = True
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets = []
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        uid = services[2]
        sets = [{'uid': uid}]
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = False
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = True
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets = []
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))

        # AR with profile with no changes
        values['Profile'] = self.analysisprofile.UID()
        ar = create_analysisrequest(client, request, values, services)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(services[0]))
        self.assertFalse(ar.getAnalysisServiceSettings(services[1]).get('hidden'))
        self.assertTrue(ar.getAnalysisServiceSettings(services[2]).get('hidden'))
        uid = services[0]
        sets = [{'uid': uid}]
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        sets[0]['hidden'] = False
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = True
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets = []
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        uid = services[1]
        sets = [{'uid': uid}]
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        sets[0]['hidden'] = False
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = True
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets = []
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        uid = services[2]
        sets = [{'uid': uid}]
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = False
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = True
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets = []
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))

        # AR with profile and template, without changes
        values['Profile'] = self.analysisprofile.UID()
        values['Template'] = self.artemplate.UID()
        ar = create_analysisrequest(client, request, values, services)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(services[0]))
        self.assertFalse(ar.getAnalysisServiceSettings(services[1]).get('hidden'))
        self.assertTrue(ar.getAnalysisServiceSettings(services[2]).get('hidden'))
        uid = services[0]
        sets = [{'uid': uid}]
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        sets[0]['hidden'] = False
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = True
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets = []
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        uid = services[1]
        sets = [{'uid': uid}]
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        sets[0]['hidden'] = False
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = True
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets = []
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))
        uid = services[2]
        sets = [{'uid': uid}]
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = False
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets[0]['hidden'] = True
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get('hidden'))
        sets = []
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse('hidden' in ar.getAnalysisServiceSettings(uid))

        # AR with profile, with changes
        values['Profile'] = self.analysisprofile.UID()
        del values['Template']
        matrix = [[0, 1,-1],  # AS = Not set
                  [0, 1, 0],  # AS = False
                  [0, 1, 1]]
        uid = services[0]
        for i in matrix:
            sets = {'uid': services[i]}
            opts = [0, 1, 2]
            for j in opts:
                if j == 0:
                    sets['hidden'] = False
                elif j == 1:
                    sets['hidden'] = True
                else:
                    del sets['hidden']
                self.analysisprofile.setAnalysesSettings(sets)
                ar = create_analysisrequest(client, request, values, services)

                res = matrix[j]
                if res == 0:
                    self.assertFalse(ar.getAnalysisServiceSettings(services[i]).get('hidden'))
                elif res == 1:
                    self.assertTrue(ar.getAnalysisServiceSettings(services[i]).get('hidden'))
                elif res == -1:
                    self.assertFalse('hidden' not in ar.getAnalysisServiceSettings(services[i]))

        # AR with template, with changes
        values['Template'] = self.artemplate.UID()
        del values['Profile']
        matrix = [[0, 1,-1],  # AS = Not set
                  [0, 1, 0],  # AS = False
                  [0, 1, 1]]
        uid = services[0]
        for i in matrix:
            sets = {'uid': services[i]}
            opts = [0, 1, 2]
            for j in opts:
                if j == 0:
                    sets['hidden'] = False
                elif j == 1:
                    sets['hidden'] = True
                else:
                    del sets['hidden']
                self.artemplate.setAnalysesSettings(sets)
                ar = create_analysisrequest(client, request, values, services)

                res = matrix[j]
                if res == 0:
                    self.assertFalse(ar.getAnalysisServiceSettings(services[i]).get('hidden'))
                elif res == 1:
                    self.assertTrue(ar.getAnalysisServiceSettings(services[i]).get('hidden'))
                elif res == -1:
                    self.assertFalse('hidden' not in ar.getAnalysisServiceSettings(services[i]))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHiddenAnalyses))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
