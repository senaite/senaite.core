# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import doctest
from os.path import join

from pkg_resources import resource_listdir

import unittest2 as unittest
from bika.lims.config import PROJECTNAME
from bika.lims.tests.base import BaseTestCase
from Testing import ZopeTestCase as ztc

rst_filenames = [f for f in resource_listdir(PROJECTNAME, "tests/doctests")
                 if f.endswith('.rst')]

doctests = [join("doctests", filename) for filename in rst_filenames]

flags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_NDIFF


def test_suite():
    suite = unittest.TestSuite()
    for doctestfile in doctests:
        suite.addTests([
            ztc.ZopeDocFileSuite(
                doctestfile,
                test_class=BaseTestCase,
                optionflags=flags
            )
        ])
    return suite
