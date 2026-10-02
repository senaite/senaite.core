Upgrade console
---------------

`senaite-upgrade` runs GenericSetup upgrade steps one at a time, from one
step to another, or re-runs a specific step. It is meant for deployments
that are only reachable over SSH, where the upgrade view in the management
interface cannot be used.

Start it against a stopped instance, optionally preselecting a profile:

.. code-block:: console

   $ bin/instance stop
   $ bin/senaite-upgrade
   $ bin/senaite-upgrade --profile my.lims:default

If the database holds more than one site, pass `-s <site-id>`. `-v`
turns on verbose (DEBUG) log capture.

Commands
~~~~~~~~

.. code-block:: text

   profiles [all]       Profiles with pending upgrades. 'all' lists every
                        profile that has upgrade steps registered.
   select <profile_id>  Choose the profile to work on.
   list [all]           List pending steps. 'all' also shows applied steps.
                        '[ ]' marks a pending step, '[x]' an applied one.
   run <spec>           Run selected step(s) in order. <spec> is 1-based:
                        'run 2', 'run 2-5', 'run 1,3,5'.
   all                  Run every pending step for the profile in order.
   debug <n>            Run a single step under pdb/pdbpp, stopping at the
                        first line of the step handler.
   version [<v>]        Show or set the profile's last applied version.

Each step is timed and its log output captured, so `history` and `log`
report what happened.

Running steps
~~~~~~~~~~~~~

A typical run selects a profile, runs the pending steps and commits:

.. code-block:: text

   (upgrade) select my.lims:default
   Selected my.lims:default (current version 1.0.3)
   Pending upgrade steps:
   [ ]   1  1.0.3 -> 1.0.4  Add a foo catalog index ...

   (upgrade* my.lims:default) run 1
   OK   1.0.3 -> 1.0.4  Add a foo catalog index ...  (0.02s, 6 log lines)
        profile my.lims:default now at version 1.0.4

   (upgrade* my.lims:default) commit
   Transaction committed.

Use `run 2-5` for a contiguous range and `run 1,3` to pick individual
steps. `all` runs every pending step in one go.

Running a step sets the profile version to that step's destination, exactly
as the management interface does. Applied steps are hidden from `list`
because they are no longer pending; show them with `list all` and run one
by its index to re-run it. Re-running an older step therefore moves the
profile version back to that step. To return to the latest version, run the
remaining steps forward or set it with `version`.

If a profile is stranded, its version sitting above a step that never ran so
the step is skipped, lower the version with `version` and the step becomes
pending again.

Debugging a failure
~~~~~~~~~~~~~~~~~~~~~

A failing step is timed, its traceback printed, and it is rolled back to a
savepoint taken just before it ran. You are then offered a post mortem
debugger and asked whether to continue with the remaining steps:

.. code-block:: text

   (upgrade* my.lims:default) run 1
   FAIL 1.0.3 -> 1.0.4  ...  (0.10s)
   Traceback (most recent call last):
     ...
   Enter post mortem debugger? [y/N] y
   (Pdb++)

The rest of the transaction is untouched, so you can `abort` to discard
everything or fix the code and re-run the step. `debug <n>` runs a step
under the debugger from the start, stopping at the first line of the
handler.

Non-interactive use
~~~~~~~~~~~~~~~~~~~~~

The same actions are available as one-shot flags for scripting:

.. code-block:: console

   # list pending steps and exit
   $ bin/senaite-upgrade --profile my.lims:default --list

   # list all steps, including applied ones
   $ bin/senaite-upgrade --profile my.lims:default --list --all

   # run steps and commit in one go
   $ bin/senaite-upgrade --profile my.lims:default --run 1-3 --commit

Without `--commit` a `--run` invocation leaves the transaction
uncommitted and reminds you to re-run with `--commit` to persist it.
