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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import doctest
from os.path import join

from pkg_resources import resource_listdir

import unittest2 as unittest
from senaite.core.config import PROJECTNAME
from senaite.core.tests.base import BaseTestCase
from Testing import ZopeTestCase as ztc
from z3c.form import testing

filenames = [f for f in resource_listdir(PROJECTNAME, "schema")
             if f.endswith(".txt")]

doctests = [join("../schema", filename) for filename in filenames]

flags = doctest.ELLIPSIS | \
        doctest.NORMALIZE_WHITESPACE | \
        doctest.IGNORE_EXCEPTION_DETAIL


def test_suite():
    suite = unittest.TestSuite()
    for doctestfile in doctests:
        suite.addTests([
            ztc.ZopeDocFileSuite(
                doctestfile,
                test_class=BaseTestCase,
                optionflags=flags,
                checker=testing.outputChecker,
            )
        ])
    return suite
