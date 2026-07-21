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

from senaite.core.scripts import parser
from senaite.core.scripts._console import ask
from senaite.core.scripts._console import BaseConsole
from senaite.core.scripts._console import bootstrap
from senaite.core.scripts._console import finish_noninteractive
from senaite.core.scripts._console import get_debugger

__doc__ = """Run SENAITE profile upgrade steps interactively and one by one.

This opens a controlled console where upgrade steps can be listed, run
step by step or from one step to another, re-run on demand and inspected
with pdb/pdbpp or IPython. Nothing is committed automatically: commit or
abort the transaction explicitly when you are done.
"""

parser.description = __doc__
parser.add_argument("--profile", dest="profile", default=None, type=str,
                    help="Preselect a profile id (e.g. my.lims:default)")
parser.add_argument("--list", dest="do_list", action="store_true",
                    help="List pending upgrade steps and exit")
parser.add_argument("--all", dest="show_old", action="store_true",
                    help="With --list, include already applied steps")
parser.add_argument("--run", dest="do_run", default=None, type=str,
                    help="Run step(s) by index/range (e.g. 1, 2-4, 1,3) "
                         "then exit")
parser.add_argument("--commit", dest="do_commit", action="store_true",
                    help="Commit the transaction after a non-interactive run")

INTRO = """
SENAITE interactive upgrade console
Type 'help' or '?' for the list of commands, 'help <cmd>' for details.
Nothing is committed until you type 'commit'. 'quit' warns if uncommitted.
"""


def flatten_upgrades(infos):
    """listUpgrades returns dicts and sub-lists of dicts. Flatten them to
    a single ordered list of step info dicts.
    """
    steps = []
    for info in infos:
        if isinstance(info, list):
            steps.extend(info)
        else:
            steps.append(info)
    return steps


def get_steps(setup_tool, profile_id, show_old=False):
    """Return the ordered, flattened list of upgrade step infos
    """
    infos = setup_tool.listUpgrades(profile_id, show_old=show_old)
    return flatten_upgrades(infos)


def version_string(version):
    """Render a profile version (tuple or string) for display
    """
    if isinstance(version, tuple):
        return ".".join(version)
    return str(version)


def format_step(index, info, pending):
    """Render one upgrade step as a table row. 'pending' marks a step that
    still needs to run given the profile's current version.
    """
    step = info["step"]
    marker = " " if pending else "x"
    return "[{0}] {1:>3}  {2} -> {3}  {4}  ({5})".format(
        marker, index, info["ssource"], info["sdest"],
        info["title"], step.id)


def parse_indices(spec, count):
    """Parse an index spec like '2', '2-4' or '1,3,5' into 0-based indices
    within [0, count). Raises ValueError on a bad or out of range token.
    """
    indices = []
    for token in spec.replace(" ", "").split(","):
        if not token:
            continue
        if "-" in token:
            low, high = token.split("-", 1)
            rng = range(int(low), int(high) + 1)
        else:
            rng = [int(token)]
        for number in rng:
            if number < 1 or number > count:
                raise ValueError("index %d out of range 1..%d"
                                 % (number, count))
            indices.append(number - 1)
    return indices


class UpgradeConsole(BaseConsole):
    """Interactive console to drive GenericSetup upgrade steps
    """

    intro = INTRO
    tool_name = "upgrade"

    def __init__(self, app, site, verbose=False):
        self.profile_id = None
        self.listing = []
        self.setup = site.portal_setup
        BaseConsole.__init__(self, app, site, verbose=verbose)

    # -- hooks -----------------------------------------------------------

    def context_label(self):
        return self.profile_id or "no profile"

    def on_site_changed(self):
        self.setup = self.site.portal_setup
        self.profile_id = None
        self.listing = []

    # -- helpers ---------------------------------------------------------

    def _require_profile(self):
        return self._require_selection(
            self.profile_id,
            "No profile selected. Use 'select <profile_id>' (see 'profiles').")

    def _refresh_listing(self, show_old=False):
        self.listing = get_steps(self.setup, self.profile_id, show_old)
        return self.listing

    def _pending_step_ids(self):
        """Ids of the steps still pending for the profile's current version.
        This is the authoritative pending signal: the 'proposed' flag from a
        show_old listing reports every step as proposed and cannot be
        trusted.
        """
        steps = get_steps(self.setup, self.profile_id, show_old=False)
        return set(info["step"].id for info in steps)

    def _print_listing(self):
        if not self.listing:
            print("No steps to show. Run 'list' or 'list all' first.")
            return
        pending = self._pending_step_ids()
        for index, info in enumerate(self.listing, start=1):
            is_pending = info["step"].id in pending
            print(format_step(index, info, is_pending))

    def _selected_infos(self, arg):
        """Resolve an index spec argument against the current listing
        """
        if not self.listing:
            self._refresh_listing(show_old=False)
        if not self.listing:
            print("No upgrade steps available for this profile.")
            return None
        try:
            indices = parse_indices(arg, len(self.listing))
        except ValueError as exc:
            print("Invalid selection: %s" % exc)
            return None
        return [self.listing[i] for i in indices]

    def _set_version(self, info):
        """Set the profile version to the step's destination after it runs,
        mirroring GenericSetup.manage_doUpgrades in the ZMI. Running a step
        always moves the recorded version to that step's dest, so re-running
        an older step moves the profile back to that step just as the web UI
        does.
        """
        dest = info["step"].dest
        if dest is None:
            return
        self.setup.setLastVersionForProfile(self.profile_id, dest)
        print("     profile %s now at version %s"
              % (self.profile_id, version_string(dest)))

    def _run_infos(self, infos):
        for info in infos:
            desc = "%s -> %s  %s" % (info["ssource"], info["sdest"],
                                     info["title"])
            result = self._execute(
                desc, lambda i=info: i["step"].doStep(self.setup))
            if result["ok"]:
                self._set_version(info)
                continue
            if not ask("Continue with the remaining steps?", default="n"):
                break

    # -- profile commands ------------------------------------------------

    def do_profiles(self, arg):
        """profiles [all] -- list profiles with pending upgrades.
        'all' lists every profile that has upgrade steps registered.
        """
        if arg.strip() == "all":
            ids = self.setup.listProfilesWithUpgrades()
            title = "Profiles with upgrade steps"
        else:
            ids = self.setup.listProfilesWithPendingUpgrades()
            title = "Profiles with pending upgrades"
        print("%s:" % title)
        if not ids:
            print("  (none)")
            return
        for pid in sorted(ids):
            version = version_string(self.setup.getLastVersionForProfile(pid))
            print("  %-45s at %s" % (pid, version))

    def do_select(self, arg):
        """select <profile_id> -- choose the profile to work on
        (e.g. select my.lims:default)
        """
        pid = arg.strip()
        if not pid:
            print("Usage: select <profile_id>")
            return
        if pid not in self.setup.listProfilesWithUpgrades():
            print("Unknown profile '%s'. See 'profiles all'." % pid)
            return
        self.profile_id = pid
        self.listing = []
        version = version_string(self.setup.getLastVersionForProfile(pid))
        print("Selected %s (current version %s)" % (pid, version))
        self._refresh_listing(show_old=False)
        if self.listing:
            print("Pending upgrade steps:")
            self._print_listing()
        else:
            print("No pending upgrade steps. Use 'list all' to see the "
                  "applied (old) steps you can re-run.")
        self._update_prompt()

    def do_list(self, arg):
        """list [all] -- list pending upgrade steps for the profile.
        'all' also shows already applied steps (use it to re-run one).
        The leftmost column marks pending steps with a space and applied
        steps with 'x'.
        """
        if not self._require_profile():
            return
        show_old = arg.strip() == "all"
        self._refresh_listing(show_old=show_old)
        self._print_listing()

    def do_run(self, arg):
        """run <spec> -- run selected step(s) from the current list.
        <spec> is 1-based: 'run 2', 'run 2-5', 'run 1,3,5'. Steps run in
        order; each is timed and its logs captured. A failing step is
        rolled back to a savepoint and you are offered a post mortem.
        To re-run an applied step, do 'list all' first, then 'run <n>'.
        """
        if not self._require_profile():
            return
        if not arg.strip():
            print("Usage: run <spec> (e.g. run 2-4). See 'list'.")
            return
        infos = self._selected_infos(arg.strip())
        if infos:
            self._run_infos(infos)

    def do_all(self, arg):
        """all -- run every pending upgrade step for the profile in order"""
        if not self._require_profile():
            return
        infos = self._refresh_listing(show_old=False)
        if not infos:
            print("No pending upgrade steps for %s." % self.profile_id)
            return
        print("About to run %d pending step(s) for %s."
              % (len(infos), self.profile_id))
        if ask("Proceed?", default="y"):
            self._run_infos(list(infos))

    def do_debug(self, arg):
        """debug <n> -- run a single step under pdb/pdbpp. The debugger
        stops at the first line of the step handler so you can step
        through it. Use 'list'/'list all' first to get the index.
        """
        if not self._require_profile():
            return
        infos = self._selected_infos(arg.strip())
        if not infos:
            return
        if len(infos) != 1:
            print("debug takes a single step index.")
            return
        info = infos[0]
        print("Entering debugger at the step handler. 'c' to run, 'q' to "
              "abort.")
        get_debugger().runcall(info["step"].doStep, self.setup)
        self.dirty = True
        self._set_version(info)
        self._update_prompt()

    def do_version(self, arg):
        """version [<v>] -- show or set the profile's last applied version.
        With no argument prints the current version; 'version 1.0.3' sets
        it (useful to un-strand a profile so its steps become pending).
        """
        if not self._require_profile():
            return
        target = arg.strip()
        if not target:
            current = self.setup.getLastVersionForProfile(self.profile_id)
            print("%s is at version %s"
                  % (self.profile_id, version_string(current)))
            return
        version = tuple(target.split("."))
        self.setup.setLastVersionForProfile(self.profile_id, version)
        self.dirty = True
        print("Set %s to version %s" % (self.profile_id, target))
        self._refresh_listing(show_old=False)
        self._update_prompt()


def run_noninteractive(console, args):
    """Handle --list / --run one-shot invocations, then optionally commit
    """
    if not args.profile:
        print("--list/--run require --profile <profile_id>")
        return
    console.do_select(args.profile)
    if args.do_list:
        console.do_list("all" if args.show_old else "")
        return
    if args.do_run:
        console.do_run(args.do_run)
        finish_noninteractive(console, args.do_commit)


def run(app):
    args, _ = parser.parse_known_args()
    site = bootstrap(app, args)
    console = UpgradeConsole(app, site, verbose=args.verbose)

    if args.do_list or args.do_run:
        run_noninteractive(console, args)
        return

    if args.profile:
        console.do_select(args.profile)
    console.cmdloop()


if __name__ == "__main__":
    run(app)  # noqa: F821
