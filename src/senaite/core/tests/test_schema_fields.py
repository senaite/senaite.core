# -*- coding: utf-8 -*-

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
