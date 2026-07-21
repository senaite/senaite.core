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

from bika.lims import api
from bika.lims.api import security as sapi
from bika.lims.api import user as uapi
from senaite.core.scripts import parser
from senaite.core.scripts._console import ask
from senaite.core.scripts._console import BaseConsole
from senaite.core.scripts._console import bootstrap

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

    def __init__(self, app, site, verbose=False):
        # the subject selected with 'select': its kind ("user"/"group"/
        # "plugin"), its id, and its numbered toggle rows. Each row is a
        # (row_kind, payload, label) tuple that 'toggle <n>' knows how to flip.
        self.subject_kind = None
        self.subject_id = None
        self.subject_rows = []
        BaseConsole.__init__(self, app, site, verbose=verbose)

    # -- hooks -----------------------------------------------------------

    def context_label(self):
        if not self.subject_kind:
            return ""
        return "%s:%s" % (self.subject_kind, self.subject_id)

    def on_site_changed(self):
        self._clear_selection()

    def _clear_selection(self):
        self.subject_kind = None
        self.subject_id = None
        self.subject_rows = []

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

    def _user_properties(self, uid):
        """(fullname, email) for a user, empty strings when unset"""
        member = self._membership().getMemberById(uid)
        if member is None:
            return "", ""
        return (member.getProperty("fullname", "") or "",
                member.getProperty("email", "") or "")

    # -- atomic mutations (single source of truth for both the explicit --
    # -- commands and the select/toggle model) ---------------------------

    def _set_user_role(self, uid, role, granted):
        prm = self._acl().portal_role_manager
        if granted:
            prm.assignRoleToPrincipal(role, uid)
        else:
            prm.removeRoleFromPrincipal(role, uid)

    def _set_group_member(self, gid, uid, member):
        if member:
            uapi.add_group(gid, uid)
        else:
            uapi.del_group(gid, uid)

    def _set_group_role(self, gid, role, granted):
        roles = set(uapi.get_group(gid).getRoles())
        if granted:
            roles.add(role)
        else:
            roles.discard(role)
        self._groups_tool().setRolesForGroup(gid, sorted(roles))

    def _set_plugin_interface(self, pid, iface, active):
        plugins = self._acl().plugins
        if active:
            plugins.activatePlugin(iface, pid)
        else:
            plugins.deactivatePlugin(iface, pid)

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
        fullname, email = self._user_properties(uid)
        print("  id:       %s" % uapi.get_user_id(user))
        print("  fullname: %s" % fullname)
        print("  email:    %s" % email)
        print("  roles:    %s" % ", ".join(sapi.get_roles(user)))
        print("  groups:   %s" % ", ".join(sorted(uapi.get_groups(user))))

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

        def op():
            for role in added:
                self._set_user_role(uid, role, True)
            for role in removed:
                self._set_user_role(uid, role, False)
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
                self._set_group_member(gid, uid, True)
            for uid in removed:
                self._set_group_member(gid, uid, False)
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

        def op():
            for role in added:
                self._set_group_role(gid, role, True)
            for role in removed:
                self._set_group_role(gid, role, False)
        self._execute("grouproles %s %s" % (gid, " ".join(parts[1:])), op)

    # -- plugin commands -------------------------------------------------

    def _plugin_type_map(self):
        """Return a mapping of interface short-name -> interface"""
        acl = self._acl()
        return dict((info["id"], info["interface"])
                    for info in acl.plugins.listPluginTypeInfo())

    def _plugin_ids(self):
        """Ids of the acl_users children that are PAS plugins, sorted"""
        acl = self._acl()
        return sorted(pid for pid in acl.objectIds()
                      if self._plugin_interfaces(pid))

    def _plugin_interfaces(self, pid):
        """(interface_name, interface) pairs the plugin implements, sorted"""
        acl = self._acl()
        plugin = getattr(acl, pid, None)
        pairs = [(info["id"], info["interface"])
                 for info in acl.plugins.listPluginTypeInfo()
                 if info["interface"].providedBy(plugin)]
        return sorted(pairs, key=lambda pair: pair[0])

    def _active_count(self, pid):
        """Number of interfaces the plugin is currently active for"""
        acl = self._acl()
        return sum(1 for _, iface in self._plugin_interfaces(pid)
                   if pid in acl.plugins.listPluginIds(iface))

    def do_plugins(self, arg):
        """plugins -- list acl_users plugins with their active interface
        count. Use 'select plugin <id>' to manage one.
        """
        acl = self._acl()
        for pid in self._plugin_ids():
            marker = "*" if (self.subject_kind == "plugin"
                             and pid == self.subject_id) else " "
            meta = getattr(getattr(acl, pid, None), "meta_type", "?")
            print(" %s %-22s %-28s %d active interface(s)"
                  % (marker, pid, meta, self._active_count(pid)))

    # -- unified subject selection ---------------------------------------

    def _valid_roles(self):
        """Assignable global roles, sorted (excludes the dynamic ones)"""
        skip = ("Anonymous", "Authenticated")
        return sorted(r for r in self.site.valid_roles() if r not in skip)

    def _subject_exists(self, kind, sid):
        if kind == "user":
            return uapi.get_user(sid) is not None
        if kind == "group":
            return uapi.get_group(sid) is not None
        if kind == "plugin":
            return sid in self._plugin_ids()
        return False

    def _add_row(self, row_kind, payload, label, active):
        """Append a numbered [X]/[ ] toggle row and print it"""
        num = len(self.subject_rows) + 1
        self.subject_rows.append((row_kind, payload, label))
        print("    [%s] %3d  %s" % ("X" if active else " ", num, label))

    def _add_role_rows(self, current_roles):
        """Add a numbered row per assignable role, marking the ones held"""
        held = set(current_roles)
        print("  roles:")
        for role in self._valid_roles():
            self._add_row("role", role, role, role in held)

    def _show_user(self):
        sid = self.subject_id
        user = uapi.get_user(sid)
        fullname, email = self._user_properties(sid)
        print("user %s (%s <%s>)" % (sid, fullname, email))
        self._add_role_rows(sapi.get_roles(user))
        in_groups = set(uapi.get_groups(user))
        print("  groups:")
        for gid in sorted(self._groups_tool().getGroupIds()):
            self._add_row("group", gid, gid, gid in in_groups)

    def _show_group(self):
        sid = self.subject_id
        group = uapi.get_group(sid)
        title = group.getProperty("title", "") or ""
        print("group %s (%s)" % (sid, title))
        print("  members: %s" % ", ".join(sorted(group.getMemberIds())))
        self._add_role_rows(group.getRoles())

    def _show_plugin(self):
        sid = self.subject_id
        acl = self._acl()
        meta = getattr(getattr(acl, sid, None), "meta_type", "?")
        print("plugin %s (%s)" % (sid, meta))
        ifaces = self._plugin_interfaces(sid)
        if not ifaces:
            print("  (implements no PAS plugin interfaces)")
        for iname, iface in ifaces:
            active = sid in acl.plugins.listPluginIds(iface)
            self._add_row("interface", iface, iname, active)

    def _show_subject(self):
        """Show the selected subject and its numbered [X]/[ ] toggle rows"""
        self.subject_rows = []
        {"user": self._show_user,
         "group": self._show_group,
         "plugin": self._show_plugin}[self.subject_kind]()

    def do_select(self, arg):
        """select [<kind>] <id> -- drill into a subject and list its
        toggleable items with [X] active / [ ] inactive, numbered for
        'toggle': roles and group membership for a user, roles for a group,
        interfaces for a plugin. <kind> is user, group or plugin; omit it to
        auto-detect from the id (e.g. 'select pasldap').
        """
        parts = arg.split()
        if not parts:
            return self.do_deselect("")
        if len(parts) > 2:
            print("Usage: select [<user|group|plugin>] <id>")
            return
        if len(parts) == 2:
            kind, sid = parts[0].lower(), parts[1]
            if kind not in ("user", "group", "plugin"):
                print("Kind must be one of: user, group, plugin")
                return
            if not self._subject_exists(kind, sid):
                print("No such %s: %s" % (kind, sid))
                return
        else:
            sid = parts[0]
            matches = [k for k in ("user", "group", "plugin")
                       if self._subject_exists(k, sid)]
            if not matches:
                print("No user, group or plugin with id '%s'." % sid)
                return
            if len(matches) > 1:
                print("'%s' matches %s. Disambiguate: select <kind> %s"
                      % (sid, " and ".join(matches), sid))
                return
            kind = matches[0]
        self.subject_kind = kind
        self.subject_id = sid
        self._show_subject()
        self._update_prompt()

    def do_deselect(self, arg):
        """deselect -- clear the current selection (also 'select' with no id)
        """
        if not self.subject_kind:
            print("Nothing selected.")
            return
        print("Deselected %s %s." % (self.subject_kind, self.subject_id))
        self._clear_selection()
        self._update_prompt()

    def _toggle_op(self, row_kind, payload, label):
        """Return (description, callable) that flips the given row for the
        current subject, delegating the write to an atomic setter.
        """
        sid = self.subject_id
        if row_kind == "interface":
            iface = payload
            active = sid in self._acl().plugins.listPluginIds(iface)
            verb = "deactivate" if active else "activate"
            return ("%s %s for %s" % (verb, sid, label),
                    lambda: self._set_plugin_interface(sid, iface, not active))
        if row_kind == "group":
            gid = payload
            member = gid in set(uapi.get_groups(uapi.get_user(sid)))
            if member:
                desc = "remove %s from group %s" % (sid, gid)
            else:
                desc = "add %s to group %s" % (sid, gid)
            return desc, lambda: self._set_group_member(gid, sid, not member)
        # row_kind == "role", on a user or a group
        if self.subject_kind == "user":
            has = label in set(sapi.get_roles(uapi.get_user(sid)))
            verb = "revoke" if has else "grant"
            return ("%s role %s for %s" % (verb, label, sid),
                    lambda: self._set_user_role(sid, label, not has))
        has = label in set(uapi.get_group(sid).getRoles())
        verb = "revoke" if has else "grant"
        return ("%s role %s for group %s" % (verb, label, sid),
                lambda: self._set_group_role(sid, label, not has))

    def do_toggle(self, arg):
        """toggle <n> -- flip item <n> of the selected subject (see 'select'):
        a role, a group membership or a plugin interface
        """
        if not self.subject_kind:
            print("No subject selected. "
                  "Use 'select <user|group|plugin> <id>'.")
            return
        try:
            row_kind, payload, label = self.subject_rows[int(arg.strip()) - 1]
        except (ValueError, IndexError):
            print("No such row. Re-run 'select %s %s' to see the numbers."
                  % (self.subject_kind, self.subject_id))
            return
        desc, op = self._toggle_op(row_kind, payload, label)
        if self._execute(desc, op)["ok"]:
            self._show_subject()

    def _toggle_plugin(self, arg, activate):
        verb = "activate" if activate else "deactivate"
        parts = arg.split()
        if len(parts) != 2:
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
        if activate == (pid in acl.plugins.listPluginIds(iface)):
            state = "active" if activate else "inactive"
            print("%s is already %s for %s." % (pid, state, iname))
            return
        self._execute(
            "%s %s for %s" % (verb, pid, iname),
            lambda: self._set_plugin_interface(pid, iface, activate))

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
    site = bootstrap(app, args)
    console = UsersConsole(app, site, verbose=args.verbose)
    console.cmdloop()


if __name__ == "__main__":
    run(app)  # noqa: F821
