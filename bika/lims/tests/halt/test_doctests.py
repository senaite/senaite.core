# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import doctest
import unittest

from plone.testing import layered
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

DOCTESTS = [
    'bika.lims.browser.accreditation',
    'bika.lims.browser.analysisrequest.add',
    'bika.lims.browser.bika_listing',
    'bika.lims.browser.instrument',
    'bika.lims.jsonapi.create',
    'bika.lims.jsonapi.update',
    'bika.lims.jsonapi.remove',
    'bika.lims.vocabularies',
]


def test_suite():
    suite = unittest.TestSuite()
    for module in DOCTESTS:
        suite.addTests([
            layered(doctest.DocTestSuite(module=module, optionflags=OPTIONFLAGS),
                    layer=BIKA_FUNCTIONAL_TESTING),
        ])
    return suite
