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

import getpass

from AccessControl.SecurityManagement import newSecurityManager
from bika.lims import api
from bika.lims.api import security as sapi
from bika.lims.api import user as uapi
from senaite.core import logger
from senaite.core.scripts import parser
from senaite.core.scripts._console import ask
from senaite.core.scripts._console import BaseConsole
from senaite.core.scripts._console import resolve_site
from senaite.core.scripts.utils import setup_site

__doc__ = """Manage acl_users users, groups and PAS plugins interactively.

This opens a controlled console to list, add, update and remove users and
groups and to activate or deactivate acl_users (PAS) plugins for their
interfaces. Each change runs in a savepoint and is timed; nothing is
committed automatically -- commit or abort the transaction explicitly when
you are done.
"""

parser.description = __doc__
parser.add_argument("--commit", dest="do_commit", action="store_true",
                    help="Commit the transaction after a non-interactive run")

# Cap the number of rows a search prints, so a broad match (e.g. an LDAP
# backend) does not dump thousands of rows to the terminal.
SEARCH_LIMIT = 100

# Id of the local ZODB user manager plugin that owns password storage for
# users created here. Directory-backed users (e.g. LDAP) are managed in the
# directory, not from this console.
LOCAL_USERS_PLUGIN = "source_users"

INTRO = """
SENAITE interactive user console
Type 'help' or '?' for the list of commands, 'help <cmd>' for details.
Nothing is committed until you type 'commit'. 'quit' warns if uncommitted.
"""


class UsersConsole(BaseConsole):
    """Interactive console to manage acl_users users, groups and plugins
    """

    intro = INTRO
    tool_name = "users"

    # -- tool helpers ----------------------------------------------------

    def _acl(self):
        """The site's PluggableAuthService (acl_users)"""
        return self.site.acl_users

    def _groups_tool(self):
        return api.get_tool("portal_groups")

    def _membership(self):
        return api.get_tool("portal_membership")

    def _registration(self):
        return api.get_tool("portal_registration")

    def _local_source(self):
        """The local ZODB user manager plugin, or None"""
        return getattr(self._acl(), LOCAL_USERS_PLUGIN, None)

    def _split_changes(self, tokens):
        """Split +name/-name tokens into (added, removed) lists"""
        added = [t[1:] for t in tokens if t.startswith("+") and t[1:]]
        removed = [t[1:] for t in tokens if t.startswith("-") and t[1:]]
        return added, removed

    # -- user commands ---------------------------------------------------

    def do_users(self, arg):
        """users [<search>] -- list users (optionally matching <search> in
        the id or login), capped at %d rows
        """ % SEARCH_LIMIT
        term = arg.strip()
        acl = self._acl()
        if term:
            found = acl.searchUsers(id=term) + acl.searchUsers(login=term)
        else:
            found = acl.searchUsers()
        ids = sorted(set(u["userid"] for u in found))
        if len(ids) > SEARCH_LIMIT:
            print("%d users match; showing the first %d. Narrow with a "
                  "search term." % (len(ids), SEARCH_LIMIT))
            ids = ids[:SEARCH_LIMIT]
        for uid in ids:
            print("  %-24s %s" % (uid, ", ".join(sapi.get_roles(uid))))
        print("%d user(s)" % len(ids))

    def do_user(self, arg):
        """user <id> -- show a user's fullname, email, roles and groups"""
        uid = arg.strip()
        if not uid:
            print("Usage: user <id>")
            return
        user = uapi.get_user(uid)
        if user is None:
            print("No such user: %s" % uid)
            return
        member = self._membership().getMemberById(uid)
        groups = [g.getId() for g in uapi.get_groups(user)]
        print("  id:       %s" % uapi.get_user_id(user))
        print("  fullname: %s" % (member and member.getProperty(
            "fullname", "") or ""))
        print("  email:    %s" % (member and member.getProperty(
            "email", "") or ""))
        print("  roles:    %s" % ", ".join(sapi.get_roles(user)))
        print("  groups:   %s" % ", ".join(sorted(groups)))

    def do_adduser(self, arg):
        """adduser <id> <email> [<password>] -- create a local user. Prompts
        for the password when omitted.
        """
        parts = arg.split()
        if len(parts) < 2:
            print("Usage: adduser <id> <email> [<password>]")
            return
        uid, email = parts[0], parts[1]
        password = parts[2] if len(parts) > 2 else None
        if password is None:
            password = getpass.getpass("Password for %s: " % uid)
        if not password:
            print("Aborted: empty password.")
            return

        def op():
            self._registration().addMember(
                uid, password, properties={
                    "username": uid, "email": email, "fullname": uid})
        self._execute("adduser %s" % uid, op)

    def do_deluser(self, arg):
        """deluser <id> -- remove a user"""
        uid = arg.strip()
        if not uid:
            print("Usage: deluser <id>")
            return
        if uapi.get_user(uid) is None:
            print("No such user: %s" % uid)
            return
        if not ask("Delete user '%s'?" % uid):
            return
        self._execute("deluser %s" % uid,
                      lambda: self._acl().userFolderDelUsers([uid]))

    def do_passwd(self, arg):
        """passwd <id> [<password>] -- set a local user's password. Prompts
        for the password when omitted.
        """
        parts = arg.split()
        if not parts:
            print("Usage: passwd <id> [<password>]")
            return
        uid = parts[0]
        source = self._local_source()
        if source is None or uid not in source.getUserIds():
            print("'%s' is not a local user (source_users); its password is "
                  "managed elsewhere (e.g. LDAP)." % uid)
            return
        password = parts[1] if len(parts) > 1 else None
        if password is None:
            password = getpass.getpass("New password for %s: " % uid)
        if not password:
            print("Aborted: empty password.")
            return
        self._execute("passwd %s" % uid,
                      lambda: source.updateUserPassword(uid, password))

    def do_roles(self, arg):
        """roles <id> [+Role -Role ...] -- show, grant or revoke a user's
        global roles (e.g. roles bob +LabManager -LabClerk)
        """
        parts = arg.split()
        if not parts:
            print("Usage: roles <id> [+Role -Role ...]")
            return
        uid = parts[0]
        if uapi.get_user(uid) is None:
            print("No such user: %s" % uid)
            return
        added, removed = self._split_changes(parts[1:])
        if not added and not removed:
            print("  roles: %s" % ", ".join(sapi.get_roles(uid)))
            return
        prm = self._acl().portal_role_manager

        def op():
            for role in added:
                prm.assignRoleToPrincipal(role, uid)
            for role in removed:
                prm.removeRoleFromPrincipal(role, uid)
        self._execute("roles %s %s" % (uid, " ".join(parts[1:])), op)

    # -- group commands --------------------------------------------------

    def do_groups(self, arg):
        """groups -- list the groups with their roles"""
        gtool = self._groups_tool()
        for gid in sorted(gtool.getGroupIds()):
            group = gtool.getGroupById(gid)
            print("  %-24s %s" % (gid, ", ".join(sorted(group.getRoles()))))

    def do_group(self, arg):
        """group <id> -- show a group's title, roles and members"""
        gid = arg.strip()
        if not gid:
            print("Usage: group <id>")
            return
        group = uapi.get_group(gid)
        if group is None:
            print("No such group: %s" % gid)
            return
        print("  id:      %s" % group.getId())
        print("  title:   %s" % (group.getProperty("title", "") or ""))
        print("  roles:   %s" % ", ".join(sorted(group.getRoles())))
        print("  members: %s" % ", ".join(sorted(group.getMemberIds())))

    def do_addgroup(self, arg):
        """addgroup <id> [<title>] -- create a group"""
        parts = arg.split(None, 1)
        if not parts:
            print("Usage: addgroup <id> [<title>]")
            return
        gid = parts[0]
        title = parts[1] if len(parts) > 1 else gid
        if uapi.get_group(gid) is not None:
            print("Group already exists: %s" % gid)
            return
        self._execute("addgroup %s" % gid,
                      lambda: self._groups_tool().addGroup(gid, title=title))

    def do_delgroup(self, arg):
        """delgroup <id> -- remove a group"""
        gid = arg.strip()
        if not gid:
            print("Usage: delgroup <id>")
            return
        if uapi.get_group(gid) is None:
            print("No such group: %s" % gid)
            return
        if not ask("Delete group '%s'?" % gid):
            return
        self._execute("delgroup %s" % gid,
                      lambda: self._groups_tool().removeGroups([gid]))

    def do_members(self, arg):
        """members <group> [+user -user ...] -- show or change group members
        (e.g. members analysts +bob -alice)
        """
        parts = arg.split()
        if not parts:
            print("Usage: members <group> [+user -user ...]")
            return
        gid = parts[0]
        group = uapi.get_group(gid)
        if group is None:
            print("No such group: %s" % gid)
            return
        added, removed = self._split_changes(parts[1:])
        if not added and not removed:
            print("  members: %s" % ", ".join(sorted(group.getMemberIds())))
            return

        def op():
            for uid in added:
                uapi.add_group(gid, uid)
            for uid in removed:
                uapi.del_group(gid, uid)
        self._execute("members %s %s" % (gid, " ".join(parts[1:])), op)

    def do_grouproles(self, arg):
        """grouproles <group> [+Role -Role ...] -- show, grant or revoke a
        group's global roles
        """
        parts = arg.split()
        if not parts:
            print("Usage: grouproles <group> [+Role -Role ...]")
            return
        gid = parts[0]
        group = uapi.get_group(gid)
        if group is None:
            print("No such group: %s" % gid)
            return
        added, removed = self._split_changes(parts[1:])
        if not added and not removed:
            print("  roles: %s" % ", ".join(sorted(group.getRoles())))
            return
        gtool = self._groups_tool()

        def op():
            roles = set(group.getRoles())
            roles.update(added)
            roles.difference_update(removed)
            gtool.setRolesForGroup(gid, sorted(roles))
        self._execute("grouproles %s %s" % (gid, " ".join(parts[1:])), op)

    # -- plugin commands -------------------------------------------------

    def _plugin_type_map(self):
        """Return a mapping of interface short-name -> interface"""
        acl = self._acl()
        return dict((info["id"], info["interface"])
                    for info in acl.plugins.listPluginTypeInfo())

    def do_plugins(self, arg):
        """plugins -- list acl_users plugins and the interfaces they are
        active for
        """
        acl = self._acl()
        active = {}
        for info in acl.plugins.listPluginTypeInfo():
            for pid in acl.plugins.listPluginIds(info["interface"]):
                active.setdefault(pid, []).append(info["id"])
        for pid in sorted(active):
            plugin = getattr(acl, pid, None)
            meta = getattr(plugin, "meta_type", "?")
            print("  %-20s %-30s %s"
                  % (pid, meta, ", ".join(sorted(active[pid]))))

    def _toggle_plugin(self, arg, activate):
        parts = arg.split()
        if len(parts) != 2:
            verb = "activate" if activate else "deactivate"
            print("Usage: %s <plugin_id> <interface>" % verb)
            return
        pid, iname = parts
        acl = self._acl()
        iface = self._plugin_type_map().get(iname)
        if iface is None:
            print("Unknown interface '%s'. See 'plugins' for the names "
                  "in use." % iname)
            return
        if getattr(acl, pid, None) is None:
            print("Unknown plugin '%s'. See 'plugins'." % pid)
            return
        active = pid in acl.plugins.listPluginIds(iface)
        if activate and active:
            print("%s is already active for %s." % (pid, iname))
            return
        if not activate and not active:
            print("%s is not active for %s." % (pid, iname))
            return
        verb = "activate" if activate else "deactivate"

        def op():
            if activate:
                acl.plugins.activatePlugin(iface, pid)
            else:
                acl.plugins.deactivatePlugin(iface, pid)
        self._execute("%s %s for %s" % (verb, pid, iname), op)

    def do_activate(self, arg):
        """activate <plugin_id> <interface> -- enable a plugin for a PAS
        interface (e.g. activate pasldap IGroupIntrospection)
        """
        self._toggle_plugin(arg, True)

    def do_deactivate(self, arg):
        """deactivate <plugin_id> <interface> -- disable a plugin for a PAS
        interface (e.g. deactivate pasldap IGroupIntrospection)
        """
        self._toggle_plugin(arg, False)


def run(app):
    args, _ = parser.parse_known_args()
    user = app.acl_users.getUser("admin")
    newSecurityManager(None, user.__of__(app.acl_users))

    site = resolve_site(app, args.site_id)
    setup_site(site)
    logger.info("Using SENAITE site '%s'" % api.get_id(site))

    console = UsersConsole(app, site, verbose=args.verbose)
    console.cmdloop()


if __name__ == "__main__":
    run(app)  # noqa: F821
