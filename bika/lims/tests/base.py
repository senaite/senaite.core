# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import os
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing.bbb import PloneTestCase
from plone.protect.authenticator import AuthenticatorView
from plone.protect.authenticator import createToken
from plone.testing.z2 import Browser
from re import match

from bika.lims.testing import BASE_TESTING
from bika.lims.testing import DATA_TESTING

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


class BaseTestCase(PloneTestCase):
    """Use for test cases which do not rely on the demo data
    """
    layer = BASE_TESTING

    def setUp(self):
        super(BaseTestCase, self).setUp()

        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        # Disable plone.protect for these tests
        self.request.form["_authenticator"] = createToken()
        # During testing, CSRF protection causes failures.
        os.environ["PLONE_CSRF_DISABLED"] = "true"

    def getBrowser(self,
                   username=TEST_USER_NAME,
                   password=TEST_USER_PASSWORD,
                   loggedIn=True):

        # Instantiate and return a testbrowser for convenience
        portal_url = self.get_url(self.portal)
        browser = Browser(self.app, url=portal_url)
        browser.addHeader('Accept-Language', 'en-US')
        browser.handleErrors = False
        if loggedIn:
            browser.open(portal_url)
            browser.getControl('Login Name').value = username
            browser.getControl('Password').value = password
            browser.getControl('Log in').click()
            self.assertTrue('You are now logged in' in browser.contents)
        return browser

    def get_url(self, obj):
        scheme = "http"
        url = obj.absolute_url()
        if not url.startswith(scheme):
            url = "{}://{}".format(scheme, url)
        return url

    def getAuthenticator(self):
        tag = AuthenticatorView('context', 'request').authenticator()
        pattern = '<input .*name="(\w+)".*value="(\w+)"'
        return match(pattern, tag).groups()[1]


class DataTestCase(BaseTestCase):
    """Use for test cases which rely on the demo data
    """
    layer = DATA_TESTING
