# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.


from bika.lims.content.instrument import Instrument
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from bika.lims.utils import tmpID
from bika.lims.exportimport import instruments

import unittest

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class Test_InstrumentsAndInterfaces(BikaFunctionalTestCase):
    """
    Different tests of Intruments and assigned Import Interfaces.
    """
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(Test_InstrumentsAndInterfaces, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def tearDown(self):
        logout()
        super(Test_InstrumentsAndInterfaces, self).tearDown()

    def test_InstrumentsAndInterfaces(self):
        exims = []
        for exim_id in instruments.__all__:
            exims.append((exim_id))
        exims.append(("Fake"))

        instrument_names = self.portal.bika_setup.bika_instruments.keys()

        bsc = getToolByName(self.portal, 'bika_setup_catalog')
        ins = bsc(portal_type='Instrument', inactive_state='active')
        import pdb; pdb.set_trace()
        for instrument in ins:
            instrument= instrument.getObject()
            instrument.setImportDataInterface(exims)
            added_ones= instrument.getImportDataInterface()
            self.assertFalse(len(added_ones) == len(exims))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_InstrumentsAndInterfaces))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
