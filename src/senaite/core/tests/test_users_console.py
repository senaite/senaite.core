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

    @staticmethod
    def _row(console, row_kind, label):
        for i, (rk, payload, lb) in enumerate(console.subject_rows, start=1):
            if rk == row_kind and lb == label:
                return i
        raise AssertionError("no %s row for %r" % (row_kind, label))

    def test_select_user_toggle_role_and_group(self):
        c = self.console
        c.do_adduser("bob bob@example.com secret123")
        c.do_addgroup("analysts Analysts")
        c.do_select("bob")  # auto-detect the kind from the id
        self.assertEqual((c.subject_kind, c.subject_id), ("user", "bob"))
        c.do_toggle(str(self._row(c, "role", "Manager")))
        self.assertIn("Manager", sapi.get_roles("bob"))
        c.do_toggle(str(self._row(c, "group", "analysts")))
        self.assertIn("bob", uapi.get_group("analysts").getMemberIds())

    def test_selected_user_defaults_commands(self):
        c = self.console
        c.do_adduser("bob bob@example.com secret123")
        c.do_addgroup("analysts Analysts")
        c.do_select("bob")
        # 'roles' with no id targets the selected user
        c.do_roles("+LabManager")
        self.assertIn("LabManager", sapi.get_roles("bob"))
        # scoped_help lists the user commands for the selection
        label, names = c.scoped_help()
        self.assertEqual(label, "user 'bob'")
        self.assertIn("roles", names)
        self.assertIn("deluser", names)

    def test_selected_group_defaults_commands(self):
        c = self.console
        c.do_adduser("bob bob@example.com secret123")
        c.do_addgroup("analysts Analysts")
        c.do_select("group analysts")
        # 'members'/'grouproles' with no id target the selected group
        c.do_members("+bob")
        self.assertIn("bob", uapi.get_group("analysts").getMemberIds())
        c.do_grouproles("+LabClerk")
        self.assertIn("LabClerk", uapi.get_group("analysts").getRoles())
        label, names = c.scoped_help()
        self.assertEqual(label, "group 'analysts'")
        self.assertIn("members", names)

    def test_selected_plugin_defaults_activate(self):
        c = self.console
        acl = self.portal.acl_users
        pid = iname = iface = None
        for info in acl.plugins.listPluginTypeInfo():
            ids = acl.plugins.listPluginIds(info["interface"])
            if ids:
                pid, iname, iface = ids[0], info["id"], info["interface"]
                break
        self.assertIsNotNone(pid)
        c.do_select("plugin %s" % pid)
        # 'deactivate'/'activate' with only the interface target the plugin
        c.do_deactivate(iname)
        self.assertNotIn(pid, acl.plugins.listPluginIds(iface))
        c.do_activate(iname)
        self.assertIn(pid, acl.plugins.listPluginIds(iface))
        label, names = c.scoped_help()
        self.assertEqual(label, "plugin '%s'" % pid)
        self.assertIn("activate", names)

    def test_scoped_help_none_without_selection(self):
        self.assertIsNone(self.console.scoped_help())

    def test_deselect(self):
        c = self.console
        c.do_addgroup("g1 G1")
        c.do_select("g1")
        self.assertEqual(c.subject_kind, "group")
        c.do_deselect("")
        self.assertIsNone(c.subject_kind)
        self.assertIsNone(c.subject_id)
        self.assertEqual(c.subject_rows, [])
        # bare 'select' with no id also clears the selection
        c.do_select("g1")
        c.do_select("")
        self.assertIsNone(c.subject_kind)

    def test_select_group_toggle_role(self):
        c = self.console
        c.do_addgroup("reviewers Reviewers")
        c.do_select("group reviewers")
        self.assertEqual(c.subject_kind, "group")
        self.assertEqual(c.subject_id, "reviewers")
        c.do_toggle(str(self._row(c, "role", "Manager")))
        self.assertIn("Manager", uapi.get_group("reviewers").getRoles())

    def test_select_plugin_toggle_interface(self):
        c = self.console
        acl = self.portal.acl_users
        pid = None
        for p in c._plugin_ids():
            if c._active_count(p) > 0:
                pid = p
                break
        self.assertIsNotNone(pid)
        c.do_select(pid)  # auto-detect: a plugin id
        self.assertEqual((c.subject_kind, c.subject_id), ("plugin", pid))
        n = iface = None
        for i, (rk, payload, lb) in enumerate(c.subject_rows, start=1):
            if rk == "interface" and pid in acl.plugins.listPluginIds(payload):
                n, iface = i, payload
                break
        self.assertIsNotNone(n)
        c.do_toggle(str(n))
        self.assertNotIn(pid, acl.plugins.listPluginIds(iface))
        c.do_toggle(str(n))
        self.assertIn(pid, acl.plugins.listPluginIds(iface))

    def test_plugins_named_activate_deactivate(self):
        c = self.console
        acl = self.portal.acl_users
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
