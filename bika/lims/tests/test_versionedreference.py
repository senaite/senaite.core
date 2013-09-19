from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from DateTime import DateTime
from bika.lims.tests.base import BikaIntegrationTestCase
from plone.app.testing import *
import transaction
import random
import unittest


class Tests(BikaIntegrationTestCase):

    layer = BIKA_INTEGRATION_TESTING

    def setUp(self):
        BikaIntegrationTestCase.setUp(self)
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['LabManager'])
        self.client = self.portal.clients.objectValues()[0]
        self.services = self.portal.bika_setup.bika_analysisservices
        self.calcs = self.portal.bika_setup.bika_calculations
        sid = self.services.invokeFactory('AnalysisService', 'tmp')
        s1 = self.services[sid]
        s1.edit(title = 's1', Keyword = 'k1')
        s1.processForm()
        sid = self.services.invokeFactory('AnalysisService', 'tmp')
        s2 = self.services[sid]
        s2.edit(title = 's2', Keyword = 'k2')
        s2.processForm()
        sid = self.services.invokeFactory('AnalysisService', 'tmp')
        s3 = self.services[sid]
        s3.edit(title = 's3', Keyword = 'k3')
        s3.processForm()
        cid = self.calcs.invokeFactory('Calculation', 'tmp')
        c1 = self.calcs[cid]
        c1.edit(title = 'c1')
        c1.processForm()

    def make_ar(self, services):
        bsc = self.portal.bika_setup_catalog
        sampletypes = [p.getObject() for p in bsc(portal_type="SampleType")]
        samplepoints = [p.getObject() for p in bsc(portal_type="SamplePoint")]
        contacts = [c for c in self.client.objectValues() if c.portal_type == 'Contact']
        sample_id = self.client.invokeFactory(type_name='Sample', id='tmp')
        sample = self.client[sample_id]
        sample.edit(
            SampleID=sample_id,
            SampleType=random.choice(sampletypes).Title(),
            SamplePoint=random.choice(samplepoints).Title(),
            ClientReference=chr(random.randint(70, 90)) * 3,
            ClientSampleID=chr(random.randint(70, 90)) * 3,
            SamplingDate=DateTime()
        )
        sample.processForm()
        ar_id = self.client.invokeFactory("AnalysisRequest", id='tmp')
        ar = self.client[ar_id]
        ar.edit(
            RequestID=ar_id,
            Contact=contacts[0],
            CCContact=contacts[1],
            CCEmails="",
            Sample=sample,
            ClientOrderNumber=chr(random.randint(70, 90)) * 3
        )
        ar.processForm()
        prices = dict([(s.UID(), '10.00') for s in services])
        ar.setAnalyses([s.UID() for s in services], prices=prices)
        return ar

    def test_versionedreference(self):

        pr = getToolByName(self.portal, 'portal_repository')
        bsc = self.portal.bika_setup_catalog

        c1 = bsc(title='c1')[0].getObject()
        s1 = bsc(title='s1')[0].getObject()
        s2 = bsc(title='s2')[0].getObject()
        s3 = bsc(title='s3')[0].getObject()

        # link service to c1:0
        s1.edit(Calculation=c1)
        self.assertEqual(s1['reference_versions'][c1.UID()], c1.version_id)
        self.assertEqual(1, c1.version_id)

        ar1 = self.make_ar([s1, ])

        # AR should link s1:0 -> c1:0
        self.assertEqual(1, ar1[s1.getKeyword()].getService().version_id)
        self.assertEqual(1, ar1[s1.getKeyword()].getService().getCalculation().version_id)

        # edit C1
        # c1 version goes up by 1
        c1.edit(DependentServices=[s2, ])
        pr.save(obj=c1,comment="Depends on S2")
        self.assertEqual(2, c1.version_id)
        transaction.get().commit()

        # c1 version goes up again
        c1 = bsc(title='c1')[0].getObject()
        c1.edit(DependentServices=[s2, s3])
        pr.save(obj=c1,comment="Depends on S2 and S3")
        self.assertEqual(3, c1.version_id)
        transaction.get().commit()

        # ar1 should still link to old calculation
        self.assertEqual(1, ar1['k1'].getService().version_id)
        self.assertEqual(1, ar1['k1'].getService().getCalculation().version_id)

        # new AR should link to new calculation
        s1 = bsc(title='s1')[0].getObject()
        ar2 = self.make_ar([s1, ])
        self.assertEqual(3, ar2['k1'].getService().version_id)
        self.assertEqual(3, ar2['k1'].getService().getCalculation().version_id)

        transaction.get().commit()

        # c1 version goes up again
        c1 = bsc(title='c1')[0].getObject()
        c1.edit(DependentServices=[s2, ])
        pr.save(obj=c1,comment="Depends on S2")
        self.assertEqual(4, c1.version_id)
        transaction.get().commit()

        # new AR should link to new calculation
        s1 = bsc(title='s1')[0].getObject()
        ar3 = self.make_ar([s1, ])
        self.assertEqual(4, ar3['k1'].getService().version_id)
        self.assertEqual(4, ar3['k1'].getService().getCalculation().version_id)



# def test_suite():
#     suite = unittest.TestSuite()
#     suite.addTest(unittest.makeSuite(Tests))
#     suite.layer = BIKA_INTEGRATION_TESTING
#     return suite
