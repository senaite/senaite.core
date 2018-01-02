# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import os
from re import match

import transaction
from plone.app.testing import DEFAULT_LANGUAGE
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from plone.app.testing import logout
from plone.protect.authenticator import AuthenticatorView
from plone.testing.z2 import Browser

from bika.lims import logger
from bika.lims.exportimport.load_setup_data import LoadSetupData
from bika.lims.testing import BIKA_LIMS_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


class BikaFunctionalTestCase(unittest.TestCase):
    layer = BIKA_LIMS_FUNCTIONAL_TESTING

    def setUp(self):
        super(BikaFunctionalTestCase, self).setUp()

        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()

        # During testing, CSRF protection causes failures.
        os.environ["PLONE_CSRF_DISABLED"] = "true"

    def getBrowser(self,
            username=TEST_USER_NAME,
            password=TEST_USER_PASSWORD,
            loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser(self.portal)
        browser.addHeader('Accept-Language', 'en-US')
        browser.handleErrors = False
        if loggedIn:
            browser.open(self.portal.absolute_url())
            browser.getControl('Login Name').value = username
            browser.getControl('Password').value = password
            browser.getControl('Log in').click()
            self.assertTrue('You are now logged in' in browser.contents)
        return browser

    def setup_data_load(self):
        transaction.commit()
        login(self.portal.aq_parent, SITE_OWNER_NAME)  # again

        # load test data
        self.request.form['setupexisting'] = 1
        self.request.form['existing'] = "bika.lims:test"
        lsd = LoadSetupData(self.portal, self.request)
        logger.info('Loading datas...')
        lsd()
        logger.info('Loading data finished...')
        logout()

    def getAuthenticator(self):
        tag = AuthenticatorView('context', 'request').authenticator()
        pattern = '<input .*name="(\w+)".*value="(\w+)"'
        return match(pattern, tag).groups()[1]
