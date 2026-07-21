Console scripts
===============

`senaite.core` ships a set of console scripts, generated as entry points
by buildout under `bin/`. Each boots Zope outside the web server, opens
the ZODB, sets up an administrative security context and runs against the
site. Because they open the database directly, the instance must be stopped
first: the file storage lock is exclusive.

Three of them, `senaite-upgrade`, `senaite-catalog` and `senaite-users`,
are interactive consoles for controlled maintenance from a plain SSH
terminal, where the management interface is not reachable. They share the
same model: pick a target, run an operation that is timed and whose log
output is captured, decide whether it succeeded, and commit or abort the
transaction by hand. Nothing is committed automatically.

These consoles share these commands:

.. code-block:: text

   commit           Commit the current transaction to the database.
   abort            Roll back all uncommitted changes.
   log [<n>]        Print the captured log of the last operation, or of
                    the nth entry in the history.
   history          Operations run this session, with status and duration.
   pdb              Drop into a pdb/pdbpp prompt.
   ipython          Open an IPython shell.
   clear            Clear the terminal screen.
   sites / site     List the sites, or switch to another one.
   quit             Leave the console (warns about uncommitted changes).

The prompt shows the selected target and a `*` when there are uncommitted
changes, for example `(upgrade* my.lims:default)`. Type `help` for the
command list and `help <command>` for the details of a single command.

.. include:: upgrade_console.rst

.. include:: catalog_console.rst

.. include:: users_console.rst
