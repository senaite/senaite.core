from Products.validation import validation
from bika.lims.browser.calcs import ajaxCalculateAnalysisEntry
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from plone.app.testing import *
from plone.keyring.interfaces import IKeyManager
from plone.testing import z2
from zope.component import getUtility
from hashlib import sha1 as sha
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
        auth=hmac.new(secret, user, sha).hexdigest()
        return auth


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
