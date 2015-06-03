import os
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.browser.stickers import Sticker
from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_SIMPLE_TESTING
from bika.lims.tests.base import BikaSimpleTestCase
from bika.lims.utils import tmpID
from bika.lims.utils.analysisrequest import create_analysisrequest
from bika.lims.workflow import doActionFor
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME

import unittest
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.resource.utils import queryResourceDirectory


class TestShowPartitions(BikaSimpleTestCase):

    def setUp(self):
        super(TestShowPartitions, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def tearDown(self):
        logout()
        super(TestShowPartitions, self).tearDown()

    def test_default_stickers(self):
        """https://jira.bikalabs.com/browse/WINE-44: display SampleID or
        SamplePartition ID depending on bikasetup.ShowPartitions value
        """

        folder = self.portal.bika_setup.bika_analysisservices
        services = [_createObjectByType("AnalysisService", folder, tmpID()),
                    _createObjectByType("AnalysisService", folder, tmpID())]
        services[0].processForm()
        services[1].processForm()
        services[0].edit(title="Detect Dust")
        services[1].edit(title="Detect water")
        service_uids = [s.UID for s in services]
        folder = self.portal.clients
        client = _createObjectByType("Client", folder, tmpID())
        client.processForm()
        folder = self.portal.clients.objectValues("Client")[0]
        contact = _createObjectByType("Contact", folder, tmpID())
        contact.processForm()
        contact.edit(Firstname="Bob", Surname="Dobbs", email="bobdobbs@heaven.org.za")
        folder = self.portal.bika_setup.bika_sampletypes
        sampletype = _createObjectByType("SampleType", folder, tmpID())
        sampletype.processForm()
        sampletype.edit(title="Air", Prefix="AIR")

        values = {'Client': client.UID(),
                  'Contact': contact.UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}

        for size in ["large", "small"]:

            # create and receive AR
            ar = create_analysisrequest(client, {}, values, service_uids)
            ar.bika_setup.setShowPartitions(False)
            doActionFor(ar, 'receive')
            self.assertEquals(ar.portal_workflow.getInfoFor(ar, 'review_state'), 'sample_received')
            # check sticker text
            ar.REQUEST['items'] = ar.getId()
            ar.REQUEST['template'] = "bika.lims:sticker_%s.pt"%size
            sticker = Sticker(ar, ar.REQUEST)()
            pid = ar.getSample().objectValues("SamplePartition")[0].getId()
            self.assertNotIn(pid, sticker, "Sticker must not contain partition ID %s"%pid)

            # create and receive AR
            ar = create_analysisrequest(client, {}, values, service_uids)
            ar.bika_setup.setShowPartitions(True)
            doActionFor(ar, 'receive')
            self.assertEquals(ar.portal_workflow.getInfoFor(ar, 'review_state'), 'sample_received')
            # check sticker text
            ar.REQUEST['items'] = ar.getId()
            ar.REQUEST['template'] = "bika.lims:sticker_%s.pt"%size
            sticker = Sticker(ar, ar.REQUEST)()
            pid = ar.getSample().objectValues("SamplePartition")[0].getId()
            self.assertIn(pid, sticker, "Sticker must contain partition ID %s"%pid)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestShowPartitions))
    suite.layer = BIKA_SIMPLE_TESTING
    return suite
