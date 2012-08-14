from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from bika.lims.controlpanel.bika_samplepoints import ajax_SamplePoints
from bika.lims.testing import BIKA_LIMS_INTEGRATION_TESTING
from bika.lims.tests.base import BikaIntegrationTestCase
from plone.app.testing import *
import json
import plone.protect
import unittest

class Tests(BikaIntegrationTestCase):

    def test_ajax_vocabulary(self):
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['LabManager'])

        self.workflow.setChainForPortalTypes('SamplePoint', ('bika_one_state_workflow', 'bika_inactive_workflow',))

        bsc = getToolByName(self.portal, 'bika_setup_catalog')

        lab_path = self.portal.bika_setup.bika_samplepoints
        client_path = self.portal.clients['client-1'] # happy hills

        # If a SampleType is specified, then the returned SamplePoints
        # will be filtered by the SamplePointSampleType relation:
        sp = bsc(portal_type = "SamplePoint", title = "Borehole 12")[0].getObject()
        st = bsc(portal_type = "SampleType", title = "Water")[0].getObject()
        sp.setSampleTypes(st.UID())
        st.setSamplePoints(sp.UID())

        self.request['sampletype'] = 'Water'
        self.request['term'] = "b"
        vocabulary = ajax_SamplePoints(lab_path, self.request)
        value = json.loads(vocabulary())
        self.assertEqual(len(value), 1)

        # Otherwise, all matching objects found are returned:
        # (term with len of 1, return only values that start with term)
        self.request['sampletype'] = ''
        vocabulary = ajax_SamplePoints(lab_path, self.request)
        value = json.loads(vocabulary())
        self.assertEqual(len(value), 4)

        # If term is two letters, also only return items which start with term.
        self.request['term'] = "br"
        vocabulary = ajax_SamplePoints(lab_path, self.request)
        value = json.loads(vocabulary())
        self.assertEqual(len(value), 2)

        # Otherwise, all matching objects found are returned:
        # This request is in lab context, so "happy hills borehole" is not returned.
        self.request['term'] = "hole"
        vocabulary = ajax_SamplePoints(lab_path, self.request)
        value = json.loads(vocabulary())
        self.assertEqual(len(value), 2)

        # If the request happens in the context of a Client or an
        # AnalysisRequest, objects contained inside the Client's folder
        # will be returned along with lab samplepoints.
        self.request['term'] = "hole"
        vocabulary = ajax_SamplePoints(client_path, self.request)
        value = json.loads(vocabulary())
        self.assertEqual(len(value), 3)

        # Only active items are returned.
        self.workflow.doActionFor(sp, 'deactivate')
        value = json.loads(vocabulary())
        self.assertEqual(len(value), 2)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_LIMS_INTEGRATION_TESTING
    return suite
