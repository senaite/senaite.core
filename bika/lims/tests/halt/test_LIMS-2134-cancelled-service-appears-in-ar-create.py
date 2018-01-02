# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""If ShowPrices is not true, then Invoices, prices, pricelists, should
all be hidden.
"""
import transaction
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.testing import BIKA_SIMPLE_FIXTURE
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils import tmpID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


class Test_ShowPrices(BikaFunctionalTestCase):
    def addthing(self, folder, portal_type, **kwargs):
        thing = _createObjectByType(portal_type, folder, tmpID())
        thing.unmarkCreationFlag()
        thing.edit(**kwargs)
        thing._renameAfterCreation()
        return thing

    def setUp(self):
        super(Test_ShowPrices, self).setUp()
        login(self.portal, TEST_USER_NAME)
        self.client = self.addthing(
            self.portal.clients,
            'Client', title='Happy Hills', ClientID='HH')
        contact = self.addthing(
            self.client,
            'Contact', Firstname='Rita', Lastname='Mohale')
        container = self.addthing(
            self.portal.bika_setup.bika_containers,
            'Container', title='Bottle', capacity="10 ml")
        sampletype = self.addthing(
            self.portal.bika_setup.bika_sampletypes,
            'SampleType', title='Water', Prefix='H2O')
        self.service1 = self.addthing(
            self.portal.bika_setup.bika_analysisservices,
            'AnalysisService', title='TestService', Keyword='TESTSERVICE', Accredited=True,
            Price='409')
        self.service2 = self.addthing(
            self.portal.bika_setup.bika_analysisservices,
            'AnalysisService', title='Oxygen', Keyword='O', Price='410')
        # Cancel one service
        wf = self.portal.portal_workflow
        wf.doActionFor(self.service1, 'deactivate')
        self.service1.reindexObject(idxs=['inactive_state'])
        transaction.commit()

    def tearDown(self):
        super(Test_ShowPrices, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_cancelled_ar_does_not_appear_in_batchbook(self):
        url = self.client.absolute_url() + "/ar_add"
        browser = self.getBrowser()
        browser.open(url)
        if "TestService" in browser.contents:
            self.fail("TestService service is inactive, yet appears in AR Create")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_ShowPrices))
    suite.layer = BIKA_SIMPLE_FIXTURE
    return suite
