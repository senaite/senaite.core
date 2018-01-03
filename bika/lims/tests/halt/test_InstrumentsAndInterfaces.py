# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login, logout

from bika.lims.exportimport import instruments
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase

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

        # Only Interfaces exist in the system can be assigned to an Instrument
        # Getting all interfaces and adding one with fake ID which shouldn't be
        # accepted as an Import Interface
        exims = []
        for exim_id in instruments.__all__:
            exims.append((exim_id))
        exims.append(("Fake"))

        # Getting all instruments
        bsc = getToolByName(self.portal, 'bika_setup_catalog')
        ins = bsc(portal_type='Instrument', inactive_state='active')

        for instrument in ins:
            instrument = instrument.getObject()
            instrument.setImportDataInterface(exims)
            added_ones = instrument.getImportDataInterface()
            # If length of added interfaces is equal to length of the list with
            # fake Interface ID, then test fails.
            self.assertFalse(len(added_ones) == len(exims))

        # TODO - testing of ajax function.

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_InstrumentsAndInterfaces))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
