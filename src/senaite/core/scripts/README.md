# SENAITE console scripts

This package holds the command line scripts that ship with SENAITE.CORE.
Each script is a console entry point (see `setup.py`) that boots Zope from
a `zope.conf`, opens the ZODB, sets up an admin security context and then
runs against the site. They run outside the web server, so the instance
must be stopped (the storage lock is exclusive).

| Script            | Purpose                                            |
|-------------------|----------------------------------------------------|
| `senaite-upgrade` | Interactive runner for GenericSetup upgrade steps  |
| `senaite-catalog` | Interactive reindex and rebuild of catalogs        |
| `senaite-users`   | Interactive manager for acl_users users, groups    |
|                   | and PAS plugins                                    |
| `upgrade-sites`   | Run the last upgrade step of every senaite profile |
| `reindex`         | Reindex an object path in the catalog              |
| `zope-passwd`     | Set or create a Zope emergency user                |

`senaite-upgrade` and `senaite-catalog` are interactive consoles that
share the same machinery: pick a target, run an operation that is timed
and whose log output is captured, then commit or abort by hand. The rest
of this document covers both.

## senaite-upgrade

An interactive console to run profile upgrade steps one at a time, from
one step to another, or to re-run a specific step. It is meant for a plain
SSH terminal. Nothing is committed automatically: you commit or abort the
transaction yourself when you are done.

For every step it records how long it took and the log output it produced,
tells you whether it succeeded, and lets you drop into pdb/pdbpp or IPython
to inspect a failure.

### Requirements

With a standalone `FileStorage` the instance must not be running, otherwise
opening the database fails with `zc.lockfile.LockError`. Stop it first
(`bin/instance stop`) and start the console against the free storage.

With a ZEO setup you do not stop the server: point `-c` at a ZEO client
`zope.conf` (e.g. `parts/client_reserved/etc/zope.conf`) so the console
connects through the running ZEO server as another client. The auto-lookup
already prefers `client_reserved`, then `client1`, then `instance`.

Buildout injects some `zope.conf` values as environment variables (via a
part's `environment-vars`, e.g. `ZEO_TMP` for a ZEO client's cache dir) that
are only exported by the generated runner, not by a plain shell. The console
detects such `$(NAME)` references and, for any that are unset, seeds a
throwaway temporary directory so the config parses (and the client gets its
own cache, avoiding a lock clash with a running reserved client). To use a
specific path instead, export the variable before running, e.g.
`ZEO_TMP=/path bin/senaite-upgrade`.

pdbpp and IPython are already available in the buildout, so `import pdb`
yields the enhanced prompt and the `ipython` command works.

### Getting the script

`senaite-upgrade` is a normal console entry point. Re-run buildout on the
target and it is generated as `bin/senaite-upgrade`.

If you cannot re-run buildout, copy any existing SENAITE.CORE console
script (its baked `sys.path` is identical) and change the final call:

```
cp bin/upgrade-sites bin/senaite-upgrade
# edit the last line to call:
#   sys.exit(senaite.core.scripts.upgrade())
```

### Starting it

```bash
# stop the instance first
bin/instance stop

# open the console (preselect a profile if you like)
bin/senaite-upgrade
bin/senaite-upgrade --profile my.lims:default
```

If the database has more than one SENAITE site, pass `-s <site-id>` to pick
one. `-v` turns on verbose (DEBUG) log capture.

### Commands

Type `help` or `?` for the command list and `help <cmd>` for the details
of a single command.

```
profiles [all]       Profiles with pending upgrades. 'all' lists every
                     profile that has upgrade steps registered.
select <profile_id>  Choose the profile to work on, e.g.
                     select my.lims:default
list [all]           List pending steps. 'all' also shows applied (old)
                     steps. '[ ]' marks pending, '[x]' marks applied.
run <spec>           Run selected step(s) in order. <spec> is 1-based:
                     run 2   run 2-5   run 1,3,5
all                  Run every pending step for the profile in order.
debug <n>            Run a single step under pdb/pdbpp, stopping at the
                     first line of the step handler.
version [<v>]        Show or set the profile's last applied version.
                     Setting it makes stranded steps pending again.
log [<n>]            Print the captured log of the last run, or of the
                     nth entry in the history.
history              Steps run this session with status and duration.
commit               Commit the transaction to the database.
abort                Roll back all uncommitted changes.
pdb                  Drop into pdb/pdbpp with app, site, setup bound.
ipython              Open an IPython shell with app, site, setup, portal.
sites / site <id>    List sites, or switch to another one.
quit                 Leave the console (warns about uncommitted changes).
```

The prompt shows the selected profile and a `*` when there are
uncommitted changes, for example `(upgrade* my.lims:default)`.

### Typical session

Run the pending steps of a profile, review, then commit:

```
(upgrade) profiles
Profiles with pending upgrades:
  my.lims:default   at 1.0.3

(upgrade) select my.lims:default
Selected my.lims:default (current version 1.0.3)
Pending upgrade steps:
[ ]   1  1.0.3 -> 1.0.4  Add a foo catalog index ...

(upgrade* my.lims:default) run 1
OK   1.0.3 -> 1.0.4  Add a foo catalog index ...  (0.02s, 6 log lines)
     profile my.lims:default now at version 1.0.4

(upgrade* my.lims:default) log
... captured log lines ...

(upgrade* my.lims:default) commit
Transaction committed.

(upgrade my.lims:default) quit
```

Use `run 2-5` to run a contiguous range and `run 1,3` to pick individual
steps. `all` runs every pending step in one go.

### Re-running an old step

Already applied steps are hidden from `list` because they are no longer
pending. Show them with `list all` and run one by its index:

```
(upgrade my.lims:default) list all
[x]   1  1.0.0 -> 1.0.1  Migrate bar field to DataGrid ...
[x]   2  1.0.1 -> 1.0.2  Add a foo catalog index and column
...
(upgrade my.lims:default) run 2
```

Running a step always sets the profile version to that step's destination,
exactly as the GenericSetup ZMI does. Re-running step 1 above therefore
moves the profile back to 1.0.1. To return to the latest version, run the
remaining steps forward, or set it directly with `version`.

If a profile is stranded (its version sits above a step that never ran, so
the step is skipped), lower the version and the step becomes pending
again:

```
(upgrade my.lims:default) version 1.0.3
(upgrade* my.lims:default) list
[ ]   1  1.0.3 -> 1.0.4  ...
(upgrade* my.lims:default) run 1
```

### When a step fails

The failing step is timed, its traceback is printed, and it is rolled back
to a savepoint taken just before it ran. You are then offered a post
mortem debugger and asked whether to continue with the remaining steps:

```
(upgrade* my.lims:default) run 1
FAIL 1.0.3 -> 1.0.4  ...  (0.10s)
Traceback (most recent call last):
  ...
Enter post mortem debugger? [y/N] y
(Pdb++)
```

Inspect the state, quit the debugger, fix the code, and re-run the step.
The rest of the transaction is untouched, so you can `abort` to discard
everything or fix and continue.

### Non-interactive use

The same actions are available as one-shot flags for scripting:

```bash
# list pending steps and exit
bin/senaite-upgrade --profile my.lims:default --list

# list all steps, including applied ones
bin/senaite-upgrade --profile my.lims:default --list --all

# run steps and commit in one go
bin/senaite-upgrade --profile my.lims:default --run 1-3 --commit
```

Without `--commit`, a `--run` invocation leaves the transaction
uncommitted and reminds you to re-run with `--commit` to persist it.

## senaite-catalog

An interactive console to reindex single catalog indexes or to clear and
rebuild a whole catalog. It shares the harness of `senaite-upgrade`: the
same timing, log capture, `commit`/`abort`, `log`/`history`, `pdb`,
`ipython`, `clear` and `sites`/`site` commands behave identically. Nothing
is committed until you say so.

Use it for the index and metadata layer of a catalog. To reindex a single
content object by path instead, use the `reindex` script.

### Getting the script

Same as `senaite-upgrade`: re-run buildout to generate `bin/senaite-catalog`,
or copy an existing SENAITE.CORE console script and change the final call
to `sys.exit(senaite.core.scripts.catalog())`.

### Commands

```
catalogs             List the catalogs in the site with their object count.
select <catalog_id>  Choose the catalog to work on, e.g.
                     select senaite_catalog_sample
indexes              List the indexes of the selected catalog and their
                     types, plus the metadata column count.
reindex [<idx> ...]  Reindex the given indexes, or all indexes when none
                     are given. Rebuilds index entries over every cataloged
                     object without clearing the catalog.
rebuild              Clear and rebuild the selected catalog. Empties it and
                     re-indexes every mapped object. Heavy and destructive,
                     so it asks to confirm first.
```

The shared `commit`, `abort`, `log`, `history`, `pdb`, `ipython`, `clear`,
`sites`/`site` and `quit` commands work exactly as in `senaite-upgrade`.

### Typical session

Reindex a couple of indexes after a change, review, then commit:

```
(catalog) catalogs
   portal_catalog                   53 objects
   senaite_catalog_sample           65 objects
   ...

(catalog) select senaite_catalog_sample
Selected senaite_catalog_sample (65 objects, 40 indexes, 30 metadata columns)

(catalog* senaite_catalog_sample) reindex review_state getId
OK   reindex senaite_catalog_sample [review_state, getId]  (0.12s, 3 log lines)

(catalog* senaite_catalog_sample) commit
Transaction committed.

(catalog senaite_catalog_sample) quit
```

`reindex` with no index names reindexes every index of the catalog.
`rebuild` clears the catalog and re-indexes all mapped objects, which is
the option to reach for when the catalog is inconsistent rather than just
stale.

### Non-interactive use

```bash
# list the indexes of a catalog and exit
bin/senaite-catalog --catalog senaite_catalog_sample --indexes

# reindex specific indexes and commit
bin/senaite-catalog --catalog senaite_catalog_sample \
    --reindex "review_state getId" --commit

# reindex every index and commit
bin/senaite-catalog --catalog senaite_catalog_sample --reindex --commit

# clear and rebuild a catalog and commit (no interactive confirm)
bin/senaite-catalog --catalog senaite_catalog_sample --rebuild --commit
```

Without `--commit` the transaction is left uncommitted and you are
reminded to re-run with `--commit` to persist it.

## senaite-users

An interactive console to manage `acl_users`: list, add, update and remove
users and groups, manage roles and group membership, and activate or
deactivate PAS plugins for their interfaces. It shares the same machinery as
the other consoles, so nothing is committed until you type `commit`.

```
bin/senaite-users -c parts/client_reserved/etc/zope.conf -s <site-id>
```

Users:

```
users [<search>]              # list users (optionally matching a term)
user <id>                     # show fullname, email, roles and groups
adduser <id> <email> [<pw>]   # create a local user (prompts for pw if omitted)
deluser <id>                  # remove a user
passwd <id> [<pw>]            # set a local user's password
roles <id> [+Role -Role ...]  # show / grant / revoke global roles
```

Groups:

```
groups                        # list groups with their roles
group <id>                    # show title, roles and members
addgroup <id> [<title>]       # create a group
delgroup <id>                 # remove a group
members <group> [+u -u ...]   # show / add / remove members
grouproles <group> [+R -R]    # show / grant / revoke group roles
```

Plugins (the same registry the ZMI "Plugins" tab manages):

```
plugins                       # list plugins with their active-interface count
activate <plugin> <iface>     # enable a plugin for an interface (explicit)
deactivate <plugin> <iface>   # disable a plugin for an interface (explicit)
```

Select and toggle (works across users, groups and plugins):

```
select <user|group|plugin> <id>   # drill into a subject, numbered [X]/[ ] list
toggle <n>                        # flip row <n> and re-show the list
```

`select` lists what you can toggle as a numbered `[X]` (active) / `[ ]`
(inactive) list: global roles and group membership for a user, global roles
for a group, interfaces (connectors) for a plugin. `toggle <n>` flips a row.

```
(users) select plugin pasldap
plugin pasldap (LDAP Plugin)
  [X]   1  IAuthenticationPlugin
  [X]   2  IGroupEnumerationPlugin
  [X]   3  IGroupIntrospection
  [X]   4  IGroupsPlugin
(users plugin:pasldap) toggle 3
OK   deactivate pasldap for IGroupIntrospection  (0.00s, 0 log lines)

(users) select user bob
user bob (Bob <bob@lab.com>)
  roles:
    [ ]   7  LabManager
    [X]   8  Member
  groups:
    [ ]  20  Analysts
(users user:bob) toggle 7     # grant the LabManager role
(users user:bob) toggle 20    # add bob to the Analysts group
```

`adduser`/`passwd` operate on the local ZODB user manager (`source_users`);
directory-backed users (e.g. LDAP) are managed in the directory. The plugin
toggles are handy on headless deployments, for example temporarily taking an
LDAP plugin out of group introspection during a maintenance operation:

```
select plugin pasldap    # note the row of IGroupIntrospection
toggle 3
commit
# ... run the maintenance ...
select plugin pasldap
toggle 3
commit
```
