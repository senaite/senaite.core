from Products.validation import validation
from bika.lims.browser.worksheet import WorksheetAddView
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from plone.app.testing import SITE_OWNER_NAME, TEST_USER_NAME, login, setRoles
from plone.keyring.interfaces import IKeyManager
from plone.testing import z2
from zope.component import getUtility
from hashlib import sha1
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

    def test_add_worksheet_from_template(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)
        client_1 = self.portal.clients.client_1
        workflow = self.portal.portal_workflow
        workflow.doActionFor(client_1.ar_1, 'receive')
        workflow.doActionFor(client_1.ar_2, 'receive')
        self.portal.REQUEST['REQUEST_METHOD'] = 'POST'
        self.portal.REQUEST.form = {'wstemplate': self.portal.bika_setup.bika_worksheettemplates.me.UID()}
        ws_id = self.portal.worksheets.generateUniqueId("Worksheet")
        WorksheetAddView(self.portal.worksheets, self.portal.REQUEST)()
        self.assertEqual(1, len(self.portal.worksheets.objectValues()))
        ws = self.portal.worksheets.objectValues()[0]
        self.assertEqual(ws.getMaxPositions(), 6)
        self.assertEqual(ws.getAnalyses(), 'analyses')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
