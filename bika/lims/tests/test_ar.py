from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from bika.lims.testing import BIKA_LIMS_INTEGRATION_TESTING
from bika.lims.testing import BIKA_LIMS_FIXTURE
from bika.lims.tests.base import BikaIntegrationTestCase
from plone.app.testing import *
import transaction
import unittest,random

class Tests(BikaIntegrationTestCase):

    defaultBases = (BIKA_LIMS_FIXTURE,)

    def test_AR(self):
        """ Make three ARs and run them through various workflows.
        """

        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['LabManager'])

        workflow = self.portal.portal_workflow
        workflow.setChainForPortalTypes(('Analysis',), ('bika_analysis_workflow', 'bika_worksheetanalysis_workflow', 'bika_cancellation_workflow',))
        workflow.setChainForPortalTypes(('AnalysisRequest',), ('bika_ar_workflow', 'bika_worksheetanalysis_workflow', 'bika_cancellation_workflow',))
        workflow.setChainForPortalTypes(('SamplePartition','Sample'), ('bika_sample_workflow', 'bika_cancellation_workflow',))

        profiles = ['Digestible Energy', 'Micro-Bio check', 'Micro-Bio counts']
        sampletypes = [p.getObject() for p in self.bsc(portal_type="SampleType")]
        samplepoints = [p.getObject() for p in self.bsc(portal_type="SamplePoint")]

        client = self.portal.clients['client-1'] # happy hills
        contacts = [c for c in client.objectValues() if c.portal_type == 'Contact']
        for profile in profiles:
            profile = self.bsc(portal_type='AnalysisProfile',
                               Title=profile)[0].getObject()
            profile_services = profile.getService()

            _ars = []
            sample_id = client.invokeFactory(type_name = 'Sample', id = 'tmp')
            sample = client[sample_id]
            sample.edit(
                SampleID = sample_id,
                SampleType = random.choice(sampletypes).Title(),
                SamplePoint = random.choice(samplepoints).Title(),
                ClientReference = chr(random.randint(70,90))*5,
                ClientSampleID = chr(random.randint(70,90))*5,
                SamplingDate = DateTime()
            )
            sample.processForm()
            self.assertEqual(len(sample.getId().split("-")), 2)
            ar_id = client.invokeFactory("AnalysisRequest", id = 'tmp')
            ar = client[ar_id]
            _ars.append(ar)
            ar.edit(
                RequestID = ar_id,
                Contact = contacts[0],
                CCContact = contacts[1],
                CCEmails = "",
                Sample = sample,
                Profile = profile,
                ClientOrderNumber = chr(random.randint(70,90))*10
            )
            ar.processForm()
            self.assertEqual(len(ar.getId().split("-")), 3)
            prices = {}
            service_uids = []
            for service in profile_services:
                service_uids.append(service.UID())
                prices[service.UID()] = service.getPrice()
            ar.setAnalyses(service_uids, prices = prices)

        wf = self.workflow

        def check_state(ar, desired_state):
            sample = ar.getSample()
            self.assertEqual(wf.getInfoFor(sample, 'review_state'), desired_state)
            part = sample.objectValues('SamplePartition')[0]
            self.assertEqual(wf.getInfoFor(part, 'review_state'), desired_state)
            analyses = ar.getAnalyses(full_objects=True)
            for a in analyses:
                self.assertEqual(wf.getInfoFor(a, 'review_state'), desired_state)

        # Sampling workflow enabled: Digestible Energy AR
        # ===============================================
        ar = _ars[0]
        wf.doActionFor(ar, 'sampling_workflow')

        ## XXX I don't know how to test cascading subscribers properly.
        ## check_state(ar, 'to_be_sampled')

        transaction.get().commit()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_LIMS_INTEGRATION_TESTING
    return suite
