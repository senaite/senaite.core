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

CLIENT_LANDING_PAGE = "client_landing_page"

WS_PRINT_TMPL_RECORD = "worksheet_print_templates_order"

SKIP_ANALYSES_STATES_ON_COPY = ["rejected"]

RR_SCINOTATION_RECORD = "scientific_notation_report"

# Modules the Python imports of a calculation may name on a new site: the
# mathematical ones. A site manager may allow more, e.g. `numpy`, which is
# left out as it reads and writes files.
CALCULATION_IMPORT_MODULES = [
    "cmath",
    "decimal",
    "fractions",
    "math",
    "scipy.special",
    "scipy.stats",
]

# Modules a calculation may never import from, nor from their submodules,
# whatever a site allows: they reach the system, the interpreter or the
# database
FORBIDDEN_CALCULATION_IMPORT_MODULES = [
    "__builtin__",
    "builtins",
    "cPickle",
    "codecs",
    "commands",
    "ctypes",
    "gc",
    "imp",
    "importlib",
    "inspect",
    "io",
    "marshal",
    "new",
    "operator",
    "os",
    "pickle",
    "posix",
    "pty",
    "shutil",
    "socket",
    "subprocess",
    "sys",
    "tempfile",
    "types",
    "AccessControl",
    "App",
    "OFS",
    "Products",
    "ZODB",
    "Zope2",
    "bika",
    "plone",
    "senaite",
    "transaction",
    "zope",
]
