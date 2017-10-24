# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import os

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
