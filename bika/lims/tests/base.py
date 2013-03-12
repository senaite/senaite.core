from AccessControl.SecurityManagement import newSecurityManager
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.protect.authenticator import AuthenticatorView
from plone.testing.z2 import Browser
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from re import match
from Testing.ZopeTestCase.functional import Functional

import unittest


class BikaTestCase(unittest.TestCase):

    def setUp(self):
        super(BikaTestCase, self).setUp()
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()

        setRoles(self.portal, TEST_USER_ID, ['LabManager', 'Member'])

    def setRequestMethod(self, method):
        self.app.REQUEST.set('REQUEST_METHOD', method)
        self.app.REQUEST.method = method

    def getAuthenticator(self):
        tag = AuthenticatorView('context', 'request').authenticator()
        pattern = '<input .*name="(\w+)".*value="(\w+)"'
        return match(pattern, tag).groups()[1]

    def setupAuthenticator(self):
        name, token = self.getAuthenticator()
        self.app.REQUEST.form[name] = token

    def loginAsPortalOwner(self):
        '''Use if - AND ONLY IF - you need to manipulate
           the portal object itself.
        '''
        uf = self.app.acl_users
        user = uf.getUserById(SITE_OWNER_NAME)
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def setPermissions(self, context, permissions, role="Member"):
        '''Changes the user's permissions.'''
        context.manage_role(role, permissions)


class BikaIntegrationTestCase(BikaTestCase):
    layer = BIKA_INTEGRATION_TESTING


class BikaFunctionalTestCase(Functional, BikaTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(BikaFunctionalTestCase, self).setUp()

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser(self.portal)
        browser.handleErrors = False
        if loggedIn:
            browser.open(self.portal.absolute_url())
            browser.getControl('Login Name').value = TEST_USER_NAME
            browser.getControl('Password').value = TEST_USER_PASSWORD
            browser.getControl('Log in').click()
            self.assertTrue('You are now logged in' in browser.contents)
        return browser
