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

"""Shared building blocks for the interactive SENAITE consoles.

Both senaite-upgrade and senaite-catalog run the same way: pick a target,
run an operation that is timed and whose log output is captured, decide
whether it succeeded, and commit or abort the transaction by hand. This
module holds the common machinery so each console only adds its own
domain commands.
"""

import cmd
import logging
import sys
import time
import traceback

import transaction
from bika.lims import api

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

# Loggers whose records we want to capture while an operation runs. We only
# add our handler to the root logger and raise these levels so their records
# propagate up to it (avoids duplicate capture).
CAPTURE_LOGGERS = ("", "GenericSetup", "senaite", "bika", "plone")

# Noisy log messages to drop while an operation runs. The GenericSetup
# import machinery dumps a full graphviz digraph of unresolved/circular
# dependencies on every profile reimport, which buries the useful output.
NOISE_LOGGER = "GenericSetup"
NOISE_SIGNATURES = (
    "There are unresolved or circular dependencies",
)


class LogCapture(logging.Handler):
    """Collect emitted log records so an operation's output can be reviewed
    """

    def __init__(self):
        logging.Handler.__init__(self)
        self.records = []

    def emit(self, record):
        self.records.append(record)


class NoiseFilter(logging.Filter):
    """Drop known noisy log records while an operation runs. Attached to the
    emitting logger, so a rejected record reaches neither the console nor
    the capture handler.
    """

    def filter(self, record):
        message = record.getMessage()
        for signature in NOISE_SIGNATURES:
            if signature in message:
                return False
        return True


def start_capture(verbose):
    """Attach a capture handler to the root logger and open up the levels
    of the relevant child loggers so their records propagate to it. Also
    install a filter that silences the known GenericSetup noise.
    """
    handler = LogCapture()
    root = logging.getLogger()
    root.addHandler(handler)
    level = logging.DEBUG if verbose else logging.INFO
    saved = []
    for name in CAPTURE_LOGGERS:
        lg = logging.getLogger(name)
        saved.append((lg, lg.level))
        lg.setLevel(level)
    noise = NoiseFilter()
    logging.getLogger(NOISE_LOGGER).addFilter(noise)
    return handler, saved, noise


def stop_capture(handler, saved, noise):
    """Detach the capture handler, restore levels and remove the filter
    """
    logging.getLogger(NOISE_LOGGER).removeFilter(noise)
    logging.getLogger().removeHandler(handler)
    for lg, lvl in saved:
        lg.setLevel(lvl)


def format_records(records):
    """Format captured log records into printable lines
    """
    fmt = logging.Formatter(LOG_FORMAT)
    return [fmt.format(record) for record in records]


def run_captured(func, verbose):
    """Run a no argument callable, timing it and capturing its log output.

    Exceptions are caught on purpose: these are debugging harnesses, so we
    record the traceback and hand it back to the caller to report and to
    offer a post mortem, rather than letting it abort the whole console.
    """
    handler, saved, noise = start_capture(verbose)
    result = {
        "ok": False,
        "seconds": 0.0,
        "error": None,
        "tb": None,
        "tb_obj": None,
        "records": handler.records,
    }
    start = time.time()
    try:
        func()
        result["ok"] = True
    except Exception as exc:  # noqa: harness boundary, re-surfaced below
        result["error"] = exc
        result["tb"] = traceback.format_exc()
        result["tb_obj"] = sys.exc_info()[2]
    finally:
        result["seconds"] = time.time() - start
        stop_capture(handler, saved, noise)
    return result


def get_debugger():
    """Return the pdb module. pdbpp shadows pdb when installed, so this
    already yields the enhanced prompt on this buildout.
    """
    import pdb
    return pdb


def ask(question, default="n"):
    """Ask a yes/no question and return True for yes
    """
    suffix = " [Y/n] " if default == "y" else " [y/N] "
    answer = raw_input(question + suffix).strip().lower()  # noqa: F821
    if not answer:
        answer = default
    return answer.startswith("y")


def get_site_ids(app):
    """Returns a list of available site ids
    """
    sites = app.objectValues("Plone Site")
    return list(map(api.get_id, sites))


def resolve_site(app, site_id):
    """Return the requested site, or the only/first one available
    """
    if site_id:
        if site_id not in get_site_ids(app):
            raise LookupError("No SENAITE site with id '%s'" % site_id)
        return app[site_id]
    sids = get_site_ids(app)
    if not sids:
        raise LookupError("No SENAITE site found in this database")
    return app[sids[0]]


class BaseConsole(cmd.Cmd, object):
    """Common interactive console: capture, timing, transaction control and
    debugging shells. Subclasses add their own domain commands and provide
    a context label for the prompt.
    """

    tool_name = "console"

    def __init__(self, app, site, verbose=False):
        cmd.Cmd.__init__(self)
        self.app = app
        self.site = site
        self.verbose = verbose
        self.history = []
        self.dirty = False
        self._update_prompt()

    # -- hooks for subclasses --------------------------------------------

    def context_label(self):
        """Short label shown in the prompt (e.g. the selected target)"""
        return ""

    def on_site_changed(self):
        """Called after 'site' switches the active site"""
        pass

    # -- shared helpers --------------------------------------------------

    def _update_prompt(self):
        flag = "*" if self.dirty else ""
        label = self.context_label()
        suffix = " %s" % label if label else ""
        self.prompt = "(%s%s%s) " % (self.tool_name, flag, suffix)

    def _execute(self, desc, func):
        """Run func inside a savepoint, timed and captured. Report a one
        line summary, record it in the history and, on failure, offer a post
        mortem and roll back to the state before the operation. Returns the
        result dict.
        """
        savepoint = transaction.savepoint(optimistic=True)
        result = run_captured(func, self.verbose)
        result["desc"] = desc
        self.history.append(result)
        seconds = result["seconds"]
        count = len(result["records"])
        if result["ok"]:
            self.dirty = True
            print("OK   %s  (%.2fs, %d log lines)" % (desc, seconds, count))
        else:
            print("FAIL %s  (%.2fs)" % (desc, seconds))
            print(result["tb"])
            if result["tb_obj"] and ask("Enter post mortem debugger?"):
                get_debugger().post_mortem(result["tb_obj"])
            savepoint.rollback()
            print("     rolled back to the state before this operation")
        self._update_prompt()
        return result

    # -- transaction / inspection ----------------------------------------

    def do_commit(self, arg):
        """commit -- commit the current transaction to the database"""
        transaction.commit()
        self.dirty = False
        print("Transaction committed.")
        self._update_prompt()

    def do_abort(self, arg):
        """abort -- roll back all uncommitted changes"""
        transaction.abort()
        self.dirty = False
        print("Transaction aborted (rolled back).")
        self._update_prompt()

    def do_clear(self, arg):
        """clear -- clear the terminal screen"""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    def do_log(self, arg):
        """log [<n>] -- print the captured log of the last operation, or of
        the nth entry in the history (see 'history').
        """
        if not self.history:
            print("Nothing recorded yet.")
            return
        entry = self.history[-1]
        if arg.strip():
            try:
                entry = self.history[int(arg.strip()) - 1]
            except (ValueError, IndexError):
                print("No such history entry.")
                return
        lines = format_records(entry["records"])
        if not lines:
            print("(no log output captured)")
            return
        for line in lines:
            print(line)

    def do_history(self, arg):
        """history -- show the operations run this session with status and
        duration
        """
        if not self.history:
            print("Nothing recorded yet.")
            return
        for index, entry in enumerate(self.history, start=1):
            status = "OK  " if entry["ok"] else "FAIL"
            print("%3d  %s  %s  (%.2fs, %d log lines)"
                  % (index, status, entry["desc"], entry["seconds"],
                     len(entry["records"])))

    # -- shells ----------------------------------------------------------

    def do_pdb(self, arg):
        """pdb -- drop into a pdb/pdbpp prompt with app and site bound"""
        app = self.app          # noqa: F841 bound for the debugger
        site = self.site        # noqa: F841
        get_debugger().set_trace()

    def do_ipython(self, arg):
        """ipython -- open an IPython shell with app, site and portal"""
        try:
            from IPython import embed
        except ImportError:
            print("IPython is not available in this environment.")
            return
        app = self.app          # noqa: F841 exposed in the shell namespace
        site = self.site        # noqa: F841
        portal = self.site      # noqa: F841
        embed()

    # -- site selection --------------------------------------------------

    def do_sites(self, arg):
        """sites -- list the SENAITE sites in this database"""
        for sid in get_site_ids(self.app):
            marker = "*" if sid == api.get_id(self.site) else " "
            print(" %s %s" % (marker, sid))

    def do_site(self, arg):
        """site <id> -- switch to another SENAITE site"""
        from senaite.core.scripts.utils import setup_site
        sid = arg.strip()
        if sid not in get_site_ids(self.app):
            print("Unknown site '%s'. See 'sites'." % sid)
            return
        self.site = self.app[sid]
        setup_site(self.site)
        self.on_site_changed()
        print("Switched to site '%s'" % sid)
        self._update_prompt()

    def do_quit(self, arg):
        """quit -- leave the console (warns about uncommitted changes)"""
        if self.dirty:
            if not ask("Uncommitted changes will be lost. Quit anyway?"):
                return False
        print("Bye. (nothing was committed unless you ran 'commit')")
        return True

    do_EOF = do_quit
    do_exit = do_quit
