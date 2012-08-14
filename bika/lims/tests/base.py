from Products.CMFCore.utils import getToolByName
from plone.testing.z2 import Browser
from Products.validation import validation
from Testing.makerequest import makerequest
from bika.lims.testing import BIKA_LIMS_FUNCTIONAL_TESTING
from bika.lims.testing import BIKA_LIMS_INTEGRATION_TESTING
from plone.app.testing import *
from plone.keyring.interfaces import IKeyManager
from plone.keyring.keymanager import KeyManager
from plone.testing import z2
from zope.component import provideUtility
import unittest

class BikaTestCase(unittest.TestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.request = self.layer['request'] #makerequest(self.portal.aq_parent).REQUEST

        # log all exceptions
        self.portal.error_log._ignored_exceptions = ()

        # Add an authenticator fpr plone.protect
        provideUtility(KeyManager(), IKeyManager)
        auth = self.portal.restrictedTraverse('@@authenticator').authenticator()
        self.request['_authenticator'] = auth.split('"')[5]

        self.portal_catalog = getToolByName(self.portal, 'portal_catalog')
        self.bsc = getToolByName(self.portal, 'bika_setup_catalog')
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.portal_registration = getToolByName(self.portal, 'portal_registration')
        self.portal_groups = getToolByName(self.portal, 'portal_groups')
        self.portal_membership = getToolByName(self.portal, 'portal_membership')
        self.plone_utils = getToolByName(self.portal, 'plone_utils')

class BikaIntegrationTestCase(BikaTestCase):
    layer = BIKA_LIMS_INTEGRATION_TESTING

class BikaFunctionalTestCase(BikaTestCase):
    layer = BIKA_LIMS_FUNCTIONAL_TESTING

    def browserLogin(self):
        baseurl = self.portal.absolute_url()
        browser = Browser(self.portal)
        browser.handleErrors = False
        browser.open(baseurl)
        browser.getControl(name='__ac_name').value=TEST_USER_NAME
        browser.getControl(name='__ac_password').value=TEST_USER_PASSWORD
        browser.getControl(name='submit').click()
        self.assertEqual(browser.url, baseurl, "Error, unable to authenticate")
        return browser
