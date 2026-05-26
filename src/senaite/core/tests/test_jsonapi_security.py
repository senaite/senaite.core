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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import base64
import json

import transaction
from AccessControl import Unauthorized
from bika.lims import api
from bika.lims.jsonapi import check_jsonapi_permission
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from senaite.core.tests.base import BaseTestCase
from senaite.core.tests.layers import BASE_LAYER_FIXTURE
from six.moves.urllib.parse import quote


class JSONAPILayer(PloneSandboxLayer):
    """Layer that also wires up plone.jsonapi.core so the `@@API` view
    (and its routes) is published, which is not the case in the base
    layer because z3c.autoinclude does not run during tests.
    """
    defaultBases = (BASE_LAYER_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(JSONAPILayer, self).setUpZope(app, configurationContext)
        import plone.jsonapi.core
        self.loadZCML(package=plone.jsonapi.core)


JSONAPI_FIXTURE = JSONAPILayer()
JSONAPI_TESTING = FunctionalTesting(
    bases=(JSONAPI_FIXTURE,), name="SENAITE:JSONAPISecurityTesting")


class TestJSONAPISecurity(BaseTestCase):
    """Regression tests for GHSA-jrw6-7x4q-w25j

    The state-changing JSON API routes (`update`, `update_many`, `remove`,
    `doActionFor`, `doActionFor_many`) and the user-enumeration route
    (`getusers`) must enforce the `AccessJSONAPI` permission. The `@@API`
    view itself is published with `zope2.View`, which Anonymous holds on
    the site root, so the per-route permission check is the only barrier
    against anonymous / under-privileged callers (CWE-862).

    `bika_setup` is the object the advisory PoC abused: its UID is
    resolvable, so each route reaches the permission check.

    Note: the `@@API` view wraps every route in the jsonapi error
    handler, so a route that raises `Unauthorized` answers with a JSON
    error (`"success": false`) carrying the message instead of an HTTP
    401. The state change is still prevented because the permission
    check runs before any mutation. This matches the existing,
    already-secured `create` route.
    """
    layer = JSONAPI_TESTING

    def setUp(self):
        super(TestJSONAPISecurity, self).setUp()
        self.portal_url = self.portal.absolute_url()
        self.target = self.portal.bika_setup
        self.target_uid = api.get_uid(self.target)

    def get_gated_routes(self):
        """Return (route, query) for every permission-gated API route
        """
        values = quote(json.dumps({"/bika_setup": {"Title": "hacked"}}))
        paths = quote(json.dumps(["/bika_setup"]))
        return [
            ("update", "obj_uid=%s&Title=hacked" % self.target_uid),
            ("update_many", "input_values=%s" % values),
            ("remove", "UID=%s" % self.target_uid),
            ("doActionFor", "UID=%s&action=reject" % self.target_uid),
            ("doActionFor_many", "action=reject&f=%s" % paths),
            ("getusers", "roles:list=Manager"),
        ]

    def get_authenticated_browser(self, username=TEST_USER_NAME,
                                  password=TEST_USER_PASSWORD):
        """Return a browser authenticated via HTTP Basic Auth

        Basic Auth is used on purpose: it avoids rendering the Plone
        login form (and any z3c.form widgets), keeping the test focused
        on the API permission check.
        """
        browser = self.getBrowser(loggedIn=False)
        credentials = base64.b64encode(
            "%s:%s" % (username, password))
        browser.addHeader("Authorization", "Basic %s" % credentials)
        return browser

    def open_api(self, browser, route, query):
        """Open the given API route with the passed-in query string
        """
        url = "{0}/@@API/{1}?{2}".format(self.portal_url, route, query)
        browser.open(url)

    def assert_blocked(self, browser, route, query):
        """The route must answer with an authorization failure
        """
        self.open_api(browser, route, query)
        self.assertIn('"success": false', browser.contents)
        self.assertIn("Unauthorized", browser.contents)

    def test_anonymous_is_blocked_on_all_gated_routes(self):
        """Anonymous callers must not reach any gated route
        """
        logout()
        for route, query in self.get_gated_routes():
            browser = self.getBrowser(loggedIn=False)
            self.assert_blocked(browser, route, query)

    def test_unprivileged_member_is_blocked_on_all_gated_routes(self):
        """Authenticated users without AccessJSONAPI are blocked too

        This isolates the permission check from incidental View
        protection: a plain Member can resolve the target object but
        still lacks `AccessJSONAPI`.
        """
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        transaction.commit()
        for route, query in self.get_gated_routes():
            browser = self.get_authenticated_browser()
            self.assert_blocked(browser, route, query)

    def test_getusers_gate_is_the_blocker_for_member(self):
        """The AccessJSONAPI check itself is what blocks the call

        `getusers` checks the permission on the site root, which a
        Member can view, so the answer must name the AccessJSONAPI
        permission (it cannot be incidental View protection).
        """
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        transaction.commit()
        browser = self.get_authenticated_browser()
        self.open_api(browser, "getusers", "roles:list=Manager")
        self.assertIn('"success": false', browser.contents)
        self.assertIn("Access JSON API", browser.contents)

    def test_privileged_user_passes_the_permission_gate(self):
        """A user holding AccessJSONAPI is not blocked by the gate

        Uses the non-destructive `getusers` route to confirm the gate
        does not over-block legitimate callers.
        """
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        transaction.commit()
        browser = self.get_authenticated_browser()
        self.open_api(browser, "getusers", "roles:list=Manager")
        self.assertIn('"success": true', browser.contents)

    def test_check_permission_helper_denies_anonymous(self):
        """The shared helper raises Unauthorized for anonymous callers
        """
        logout()
        self.assertRaises(
            Unauthorized, check_jsonapi_permission, self.target)

    def test_check_permission_helper_allows_privileged(self):
        """The shared helper passes for a user holding AccessJSONAPI
        """
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        # must not raise and returns None
        self.assertIsNone(check_jsonapi_permission(self.target))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestJSONAPISecurity))
    return suite
