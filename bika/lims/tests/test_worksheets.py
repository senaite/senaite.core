from Products.validation import validation
from bika.lims.browser.worksheet import WorksheetAddView
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from plone.app.testing import SITE_OWNER_NAME, TEST_USER_NAME, login, setRoles
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

    def test_add_worksheet_from_template(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)
        ar_1 = self.portal.clients.client_1.ar_1
        self.portal.portal_workflow.doActionFor(ar_1, 'receive')
        ar_2 = self.portal.clients.client_1.ar_2
        self.portal.portal_workflow.doActionFor(ar_2, 'receive')
        request = self.portal.REQUEST
        request['REQUEST_METHOD'] = 'POST'
        form = {'test_worksheet_id':'ws_1',
                'wstemplate':self.portal.bika_setup.bika_worksheettemplates.worksheettemplate_1.UID()}
        request['form'] = form
        WorksheetAddView(self.portal.worksheets, request)()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
