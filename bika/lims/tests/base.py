from Products.CMFCore.utils import getToolByName
from Testing.makerequest import makerequest
from bika.lims.testing import BIKA_LIMS_INTEGRATION_TESTING
from plone.app.testing import *
from plone.keyring.interfaces import IKeyManager
from plone.keyring.keymanager import KeyManager
from zope.component import provideUtility
import unittest

class BikaTestCase(unittest.TestCase):

    layer = BIKA_LIMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.request = makerequest(self.portal.aq_parent).REQUEST

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
