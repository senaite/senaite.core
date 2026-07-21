Users console
-------------

`senaite-users` manages the site's ``acl_users``: it lists, adds, updates
and removes users and groups, manages roles and group membership, and
activates or deactivates PAS plugins for their interfaces. It is meant for
a plain SSH terminal where the management interface is not reachable.

Start it against a stopped instance (or, on a ZEO setup, a client config):

.. code-block:: console

   $ bin/instance stop
   $ bin/senaite-users
   $ bin/senaite-users -c parts/client_reserved/etc/zope.conf -s my.lims

Commands
~~~~~~~~

.. code-block:: text

   users [<search>]              List users, optionally matching a term in
                                 the id or login (capped at 100 rows).
   user <id>                     Show fullname, email, roles and groups.
   adduser <id> <email> [<pw>]   Create a local user; prompts for the
                                 password when omitted.
   deluser <id>                  Remove a user.
   passwd <id> [<pw>]            Set a local user's password.
   roles <id> [+Role -Role ...]  Show, grant or revoke global roles.
   groups                        List groups with their roles.
   group <id>                    Show title, roles and members.
   addgroup <id> [<title>]       Create a group.
   delgroup <id>                 Remove a group.
   members <group> [+u -u ...]   Show, add or remove group members.
   grouproles <group> [+R -R]    Show, grant or revoke group roles.
   plugins                       List plugins and the interfaces they serve.
   activate <plugin> <iface>     Enable a plugin for a PAS interface.
   deactivate <plugin> <iface>   Disable a plugin for a PAS interface.

``adduser`` and ``passwd`` operate on the local ZODB user manager
(``source_users``); directory-backed users (e.g. LDAP) are managed in the
directory. Every change runs in a savepoint and is timed; nothing is
committed until you type ``commit``.

The plugin commands are useful on headless deployments. For example, to
temporarily take an LDAP plugin out of group introspection during a
maintenance operation:

.. code-block:: text

   deactivate pasldap IGroupIntrospection
   commit
   # ... run the maintenance ...
   activate pasldap IGroupIntrospection
   commit
