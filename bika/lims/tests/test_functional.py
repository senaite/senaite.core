from plone.testing import layered
import doctest
import glob
import os
import unittest

from zope.testing.doctest import DocFileSuite
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING

UNITTESTS = []  # skip these filenames
OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def list_doctests():
    return [filename for filename in
            glob.glob(os.path.sep.join([os.path.dirname(__file__), '*.rst']))
            if os.path.basename(filename) not in UNITTESTS]


def test_suite():
    filenames = list_doctests()

    suites = []
    for filename in filenames:
        filename = os.path.join("tests", os.path.basename(filename))
        suite = layered(
            DocFileSuite(
                filename,
                package='bika.lims',
                optionflags=OPTIONFLAGS
            ),
            layer=BIKA_FUNCTIONAL_TESTING
        )
        suites.append(suite)

    return unittest.TestSuite(suites)
