from Products.validation import validation
from bika.lims.browser.calcs import AJAXCalculateAnalysisEntry
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

    def test_calc(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)
        client_1 = self.portal.clients.client_1
        self.portal.portal_workflow.doActionFor(client_1.ar_2, 'receive')
        request = self.portal.REQUEST
        request['REQUEST_METHOD'] = 'POST'
        request['_authenticator'] = self._authenticator(SITE_OWNER_NAME)
        request['item_data'] = json.dumps([{'keyword':'TV', 'title':'Titr Vol', 'type':'int', 'value':10, 'unit':'g'},
                                           {'keyword':'TF', 'title':'Titr Fact', 'type':'int', 'value':10, 'unit':''}])
        request['results'] = json.dumps({client_1.ar_2.titration.UID():'0'})
        request['uid'] = client_1.ar_2.titration.UID()
        request['field'] = 'TV'
        request['value'] = '10'
        ret = json.loads(AJAXCalculateAnalysisEntry(client_1.ar_2.titration, request)())
        self.assertEqual(ret['results'][0]['result'], 100.0)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
