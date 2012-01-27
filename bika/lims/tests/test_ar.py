from Products.validation import validation
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from plone.app.testing import *
from plone.testing import z2
from Products.validation import validation as validationService
from Products.CMFCore.utils import getToolByName

import unittest

class Tests(unittest.TestCase):

    layer = BIKA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

        self.portal_catalog = getToolByName(self.portal, 'portal_catalog')
        self.bsc = bsc = getToolByName(self.portal, 'bika_setup_catalog')
        self.portal_workflow = getToolByName(self.portal, 'portal_workflow')
        self.portal_registration = getToolByName(self.portal, 'portal_registration')
        self.portal_groups = getToolByName(self.portal, 'portal_groups')
        self.portal_membership = getToolByName(self.portal, 'portal_membership')
        self.translate = getToolByName(self.portal, 'translation_service').translate
        self.plone_utils = getToolByName(self.portal, 'plone_utils')

    def test_AR(self):
        login(self.portal, TEST_USER_NAME)

        profiles = {'Digestible Energy': 2,
                    'Micro-Bio check': 2,
                    'Micro-Bio counts': 2,
                    'Trace Metals': 2}

        sampletypes = [p.getObject() for p in self.bsc(portal_type="SampleType")]
        samplepoints = [p.getObject() for p in self.bsc(portal_type="SamplePoint")]

        for client in self.context.clients.objectValues():
            contacts = [c for c in client.objectValues() if c.portal_type == 'Contact']
            for profile, count_ars in profiles.items():
                profile = self.bsc(portal_type='ARProfile',
                                   Title=profile)[0].getObject()
                profile_services = profile.getService()

                _ars = []
                t = timer()
                for i in range(1, count_ars+1):
                    _id = client.invokeFactory(type_name = 'Sample', id = 'tmp')
                    sample = client[_id]
                    sample.edit(
                        SampleID = sample_id,
                        SampleType = random.choice(sampletypes).Title(),
                        SamplePoint = random.choice(samplepoints).Title(),
                        ClientReference = "".join([chr(random.randint(70,90)) for r in range(5)]),
                        ClientSampleID = "".join([chr(random.randint(70,90)) for r in range(5)]),
                        LastARNumber = 1,
                        DateSubmitted = DateTime(),
                        DateSampled = (i == count_ars and DateTime()+86400 or DateTime()),
                        SubmittedByUser = sample.current_user()
                    )
                    sample.unmarkCreationFlag()
                    self.assertEqual(len(sample.getId().split("-")), 2)
                    ar_id = client.generateARUniqueId("AnalysisRequest", sample_id, 1)
                    client.invokeFactory("AnalysisRequest", ar_id)
                    ar = client[ar_id]
                    _ars.append(ar)
                    ar.edit(
                        RequestID = ar_id,
                        DateRequested = DateTime(),
                        Contact = contacts[0],
                        CCContact = contacts[1],
                        CCEmails = "",
                        Sample = sample,
                        Profile = profile,
                        ClientOrderNumber = "".join([chr(random.randint(70,90)) for r in range(10)]),
                    )
                    ar.unmarkCreationFlag()
                    self.assertEqual(len(ar.getId().split("-")), 2)
                    prices = {}
                    service_uids = []
                    for service in profile_services:
                        service_uids.append(service.UID())
                        prices[service.UID()] = service.getPrice()
                    ar.setAnalyses(service_uids, prices = prices)
                for i in range(2):
                    self.portal_workflow.doActionFor(_ars[i], 'receive')
                    self.assertEqual(portal_workflow.getInfoFor(_ars[i], 'review_state', ''),
                                     'sample_received')
                transaction.get().commit()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
