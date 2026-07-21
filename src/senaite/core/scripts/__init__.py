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

import argparse
import atexit
import logging
import os
import re
import shutil
import tempfile
import time
import types

from senaite.core import logger

# ZConfig resolves `$(NAME)` substitutions from the OS environment (the
# `${NAME}`/`$NAME` forms come from `%define` in the file instead). Buildout
# injects such environment variables (e.g. `ZEO_TMP` for a ZEO client cache
# directory) when it starts an instance, but a bare console run does not have
# them, so parsing the client `zope.conf` fails with
# `no replacement for '<NAME>'`. This pattern detects those references.
ENV_SUBSTITUTION_RE = re.compile(r"\$\(([a-zA-Z_][a-zA-Z0-9_]*)\)")

parser = argparse.ArgumentParser(
    description="Run a SENAITE script")
parser.add_argument("-s", "--site-id", dest="site_id", default=None,
                    help="ID of the SENAITE instance")
parser.add_argument("-c", "--config", dest="zope_conf",
                    help="Path to ZOPE configuration file")
parser.add_argument("-v", "--verbose", dest="verbose",
                    action="store_true",
                    help="Verbose logging")

this_dir = os.path.dirname(os.path.realpath(__file__))


def seed_missing_config_env(conf_path):
    """Seed `os.environ` for `$(NAME)` substitutions missing from the shell.

    The generated instance/client runner exports buildout `environment-vars`
    (e.g. `ZEO_TMP`) before Zope reads the config. A bare console run does not,
    so any `$(NAME)` referring to an unset variable makes ZConfig fail. For
    those we set a writable temporary directory (removed on exit); such
    variables are local cache/var paths that a one-shot maintenance run can
    keep to itself.
    """
    with open(conf_path) as f:
        names = set(ENV_SUBSTITUTION_RE.findall(f.read()))
    missing = sorted(name for name in names if name not in os.environ)
    if not missing:
        return
    tmp = tempfile.mkdtemp(prefix="senaite-console-")
    atexit.register(shutil.rmtree, tmp, True)
    for name in missing:
        os.environ[name] = tmp
    logger.warning(
        "Seeded missing config environment variable(s) %s -> %s "
        "(not set in this shell; using a temporary directory)",
        ", ".join(missing), tmp)


def resolve_module(module):
    """Resolve module
    """
    if isinstance(module, types.ModuleType):
        return module
    from zope.dottedname.resolve import resolve
    return resolve("senaite.core.scripts." + module)


def run_it(module):
    module = resolve_module(module)
    args, _ = parser.parse_known_args()
    cwd = os.getcwd()
    conf_path = None
    lookup_paths = [
        os.path.join(cwd, "parts/client_reserved/etc/zope.conf"),
        os.path.join(cwd, "parts/client1/etc/zope.conf"),
        os.path.join(cwd, "parts/instance/etc/zope.conf"),
    ]
    if args.zope_conf:
        lookup_paths.insert(0, args.zope_conf)
    for path in lookup_paths:
        if os.path.exists(path):
            conf_path = path
            break
    if conf_path is None:
        raise Exception("Could not find zope.conf in {}".format(lookup_paths))

    # ensure buildout-injected `$(NAME)` env vars (e.g. ZEO_TMP) are present
    seed_missing_config_env(conf_path)

    from Zope2 import configure
    configure(conf_path)
    import Zope2
    app = Zope2.app()
    from Testing.makerequest import makerequest
    app = makerequest(app)
    app.REQUEST["PARENTS"] = [app]
    from zope.globalrequest import setRequest
    setRequest(app.REQUEST)
    from AccessControl.SpecialUsers import system as user
    from AccessControl.SecurityManagement import newSecurityManager
    newSecurityManager(None, user)

    # verbose logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    start = time.time()
    module.run(app)
    end = time.time()
    logger.info("Script execution took: %.2f seconds" % float(end-start))


def zope_passwd():
    return run_it("_zope_passwd")


def upgrade_sites():
    return run_it("_upgrade_sites")


def reindex():
    return run_it("_reindex")


def upgrade():
    return run_it("_upgrade")


def catalog():
    return run_it("_catalog")


def users():
    return run_it("_users")
