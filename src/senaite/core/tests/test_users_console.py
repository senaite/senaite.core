# -*- coding: utf-8 -*-
from bika.lims.api import security as sapi
from bika.lims.api import user as uapi
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from senaite.core.scripts import _users
from senaite.core.scripts._users import UsersConsole
from senaite.core.tests.base import BaseTestCase


class TestUsersConsole(BaseTestCase):

    def setUp(self):
        super(TestUsersConsole, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        app = self.portal.aq_parent
        self.console = UsersConsole(app, self.portal)
        # stub the interactive yes/no confirm to always accept
        self._orig_ask = _users.ask
        _users.ask = lambda *a, **kw: True

    def tearDown(self):
        _users.ask = self._orig_ask
        super(TestUsersConsole, self).tearDown()

    def test_group_crud_and_members(self):
        c = self.console
        c.do_addgroup("analysts Analysts")
        self.assertIsNotNone(uapi.get_group("analysts"))
        c.do_adduser("bob bob@example.com secret123")
        self.assertIsNotNone(uapi.get_user("bob"))
        c.do_members("analysts +bob")
        self.assertIn("bob", uapi.get_group("analysts").getMemberIds())
        c.do_members("analysts -bob")
        self.assertNotIn("bob", uapi.get_group("analysts").getMemberIds())

    def test_user_roles_and_delete(self):
        c = self.console
        c.do_adduser("alice alice@example.com secret123")
        c.do_roles("alice +LabManager")
        self.assertIn("LabManager", sapi.get_roles("alice"))
        c.do_roles("alice -LabManager")
        self.assertNotIn("LabManager", sapi.get_roles("alice"))
        c.do_deluser("alice")
        self.assertIsNone(uapi.get_user("alice"))

    def test_grouproles(self):
        c = self.console
        c.do_addgroup("reviewers Reviewers")
        c.do_grouproles("reviewers +LabClerk")
        self.assertIn("LabClerk", uapi.get_group("reviewers").getRoles())

    def test_plugins_list_and_toggle(self):
        c = self.console
        c.do_plugins("")  # must not raise
        acl = self.portal.acl_users
        # find an active (plugin, interface) pair to round-trip
        pid = iname = None
        for info in acl.plugins.listPluginTypeInfo():
            ids = acl.plugins.listPluginIds(info["interface"])
            if ids:
                pid, iname = ids[0], info["id"]
                break
        self.assertIsNotNone(pid)
        c.do_deactivate("%s %s" % (pid, iname))
        self.assertNotIn(
            pid, acl.plugins.listPluginIds(c._plugin_type_map()[iname]))
        c.do_activate("%s %s" % (pid, iname))
        self.assertIn(
            pid, acl.plugins.listPluginIds(c._plugin_type_map()[iname]))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUsersConsole))
    return suite
