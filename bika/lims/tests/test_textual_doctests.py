# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import doctest

import unittest2 as unittest

from Testing import ZopeTestCase as ztc

from bika.lims.tests.base import BikaSimpleTestCase


DOCTESTS = [
    "../docs/Instruments.rst",
    "../docs/Versioning.rst",
]


def test_suite():
    suite = unittest.TestSuite()
    for doctestfile in DOCTESTS:
        suite.addTests([
            ztc.ZopeDocFileSuite(
                doctestfile,
                test_class=BikaSimpleTestCase,
                optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
            )
    ])
    return suite
