from Products.CMFCore.utils import getToolByName
from bika.lims.controlpanel.bika_samplepoints import ajax_SamplePoints
from bika.lims.tests.base import BikaIntegrationTestCase
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_ID
import json


class Tests(BikaIntegrationTestCase):

    def setUp(self):
        super(Tests, self).setUp()

    def test_ajax_vocabulary(self):
        wf = getToolByName(self.portal, "portal_workflow")
        wf.setChainForPortalTypes(
            'SamplePoint',
            ('bika_one_state_workflow', 'bika_inactive_workflow'))
        wf.setChainForPortalTypes(
            'SampleType',
            ('bika_one_state_workflow', 'bika_inactive_workflow'))

        self.portal.clients.invokeFactory('Client', 'client1',
                                          title="Client One")
        c1 = self.portal.clients.client1
        c1.unmarkCreationFlag()
        c1.invokeFactory('SamplePoint', id='csp1', title="Client Point 1")
        c1.csp1.unmarkCreationFlag()
        samplepoints = self.portal.bika_setup.bika_samplepoints
        samplepoints.invokeFactory('SamplePoint', id='sp1',
                                   title="Point AAA 1")
        samplepoints.invokeFactory('SamplePoint', id='sp2',
                                   title="Point BBB 2")
        samplepoints.sp1.unmarkCreationFlag()
        samplepoints.sp2.unmarkCreationFlag()
        sp1, sp2 = samplepoints.sp1, samplepoints.sp2
        sampletypes = self.portal.bika_setup.bika_sampletypes
        sampletypes.invokeFactory('SampleType', id='st1', title="Type AAA 1")
        sampletypes.invokeFactory('SampleType', id='st2', title="Type BBB 2")
        sampletypes.st1.unmarkCreationFlag()
        sampletypes.st2.unmarkCreationFlag()
        st1, st2 = sampletypes.st1, sampletypes.st2

        sp1.setSampleTypes([st1])
        st1.setSamplePoints([sp1])

        self.request['_authenticator'] = self.getAuthenticator()

        # Without no search term, no objects are returned.
        res = ajax_SamplePoints(samplepoints, self.request)()
        value = json.loads(res)
        self.assertEqual(len(value), 0)
        # In Client context (or in subfolders of Client), Client samplepoints
        # are included
        self.request['term'] = "Point"
        res = ajax_SamplePoints(c1, self.request)()
        value = json.loads(res)
        self.assertEqual(len(value), 3)

        # One result linked to Type AAA 1 has 'AAA' in the titles
        self.request['sampletype'] = 'Type AAA 1'
        self.request['term'] = "AAA"
        res = ajax_SamplePoints(samplepoints, self.request)()
        value = json.loads(res)
        self.assertEqual(len(value), 1)

        self.request['sampletype'] = ''
        self.request['term'] = "Po"
        res = ajax_SamplePoints(samplepoints, self.request)()
        value = json.loads(res)
        self.assertEqual(len(value), 2)

        # Only active items are returned.
        wf.doActionFor(sp2, 'deactivate')
        self.request['term'] = "Point"
        res = ajax_SamplePoints(c1, self.request)()
        value = json.loads(res)
        self.assertEqual(len(value), 2)
