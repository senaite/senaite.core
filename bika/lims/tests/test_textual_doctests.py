# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import doctest

import unittest2 as unittest
from Testing import ZopeTestCase as ztc
from bika.lims.tests.base import BikaFunctionalTestCase
from pkg_resources import resource_listdir

DOCTESTS = [f for f in resource_listdir("bika.lims", "tests/doctests")
            if f.endswith(".rst")]

flags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_NDIFF


def test_suite():
    suite = unittest.TestSuite()
    for doctestfile in DOCTESTS:
        suite.addTests([
            ztc.ZopeDocFileSuite(
                doctestfile,
                test_class=BikaFunctionalTestCase,
                optionflags=flags
            )
        ])
    return suite
