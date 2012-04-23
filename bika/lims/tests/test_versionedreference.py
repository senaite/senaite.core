from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from hashlib import sha1
from plone.app.testing import *
from plone.keyring.interfaces import IKeyManager
from plone.testing import z2
from zope.component import getUtility
import hmac
import json
import plone.protect
import unittest

class Tests(unittest.TestCase):

    layer = BIKA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

    def _authenticator(self, user):
        manager = getUtility(IKeyManager)
        secret=manager.secret()
        auth=hmac.new(secret, user, sha1).hexdigest()
        return auth

    def test_versionedreference(self):
        login(self.portal, TEST_USER_NAME)

        bsc = getToolByName(self.portal, 'bika_setup_catalog')
        moist = bsc(getKeyword = 'Moist')[0].getObject()
        weightloss = bsc(portal_type="Calculation", title="Weight Loss")[0].getObject()
        self.assertEqual(moist.getCalculation(), weightloss)
        self.assertEqual(weightloss.version_id, moist.reference_versions[weightloss.UID()])
        weightloss.setTitle("New Title")
        pr = getToolByName(self.portal, 'portal_repository')
        pr.save(obj=weightloss, comment="v1 -> v2")
        self.assertTrue(weightloss.version_id >
                        moist.reference_versions[weightloss.UID()])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
