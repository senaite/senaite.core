from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_base
from bika.lims import logger
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING, BIKA_SIMPLE_TESTING
from plone.app.robotframework.remote import RemoteLibrary
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.protect.authenticator import AuthenticatorView
from plone.testing.z2 import Browser
from Products.CMFPlone.tests.utils import MockMailHost as _MMH
from Products.MailHost.interfaces import IMailHost
from re import match
from Testing.ZopeTestCase.functional import Functional
from zope.component import getSiteManager

import unittest


class MockMailHost(_MMH):

    def send(self, *kwargs):
        logger.log("***Message***")
        logger.log("From: {0}".format(kwargs['mfrom']))
        logger.log("To: {0}".format(kwargs['mto']))
        logger.log("Subject: {0}".format(kwargs['subject']))
        logger.log("Length: {0}".format(len(kwargs['messageText'])))
        _MMH.send(self, *kwargs)


class BikaTestCase(unittest.TestCase):

    def setUp(self):
        super(BikaTestCase, self).setUp()

    def afterSetUp(self):
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        mailhost.smtp_host = 'localhost'
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        self.portal.email_from_address = 'test@example.com'
        ltool = self.portal.portal_languages
        ltool.setLanguageBindings()

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(
            aq_base(
                self.portal._original_MailHost),
            provided=IMailHost)

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

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser(self.portal)
        browser.addHeader('Accept-Language', 'en-US')
        browser.handleErrors = False
        if loggedIn:
            browser.open(self.portal.absolute_url())
            browser.getControl('Login Name').value = TEST_USER_NAME
            browser.getControl('Password').value = TEST_USER_PASSWORD
            browser.getControl('Log in').click()
            self.assertTrue('You are now logged in' in browser.contents)
        return browser


class BikaSimpleTestCase(Functional, BikaTestCase):

    layer = BIKA_SIMPLE_TESTING

    def setUp(self):
        super(BikaSimpleTestCase, self).setUp()
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['LabManager', 'Member'])

class BikaFunctionalTestCase(Functional, BikaTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(BikaFunctionalTestCase, self).setUp()
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['LabManager', 'Member'])
