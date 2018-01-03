# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFPlone.utils import _createObjectByType
from bika.lims.testing import BIKA_LIMS_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils import tmpID
from bika.lims.utils.analysis import create_analysis
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestMultiVerificationType(BikaFunctionalTestCase):
    """
    In Bika Setup, When Multi verification is enabled, one of 3 types of Multi Verification
    option should be chosen. Functional Testing of this new feature.
    """
    layer = BIKA_LIMS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestMultiVerificationType, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ['Member', 'LabManager'])
        self.setup_data_load()
        login(self.portal, TEST_USER_NAME)

    def tearDown(self):
        super(TestMultiVerificationType, self).tearDown()

    def test_MultiVerificationType(self):
        #Testing when the same user can verify multiple times
        self.portal.bika_setup.setNumberOfRequiredVerifications(4)
        self.portal.bika_setup.setTypeOfmultiVerification('self_multi_enabled')

        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2016-12-12',
                  'SampleType': sampletype.UID()}
        ar = _createObjectByType("AnalysisRequest", client, tmpID())
        servs = self.portal.bika_setup.bika_analysisservices
        service=servs['analysisservice-3']
        service.setSelfVerification(True)
        an = create_analysis(ar, service)
        member = self.portal.portal_membership.getMemberById('admin')
        an.setVerificators(member.getUserName())
        an.setNumberOfRequiredVerifications(4)
        self.assertEquals(an.isUserAllowedToVerify(member), True)

        #Testing when the same user can verify multiple times but not consequetively
        self.portal.bika_setup.setTypeOfmultiVerification('self_multi_not_cons')
        self.assertEquals(an.isUserAllowedToVerify(member), False)

        #Testing when the same user can not verify more than once
        self.portal.bika_setup.setTypeOfmultiVerification('self_multi_disabled')
        self.assertEquals(an.isUserAllowedToVerify(member), False)

        an.addVerificator(TEST_USER_NAME)
        self.portal.bika_setup.setTypeOfmultiVerification('self_multi_not_cons')
        self.assertEquals(an.isUserAllowedToVerify(member), True)

        self.portal.bika_setup.setTypeOfmultiVerification('self_multi_disabled')
        self.assertEquals(an.isUserAllowedToVerify(member), False)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMultiVerificationType))
    suite.layer = BIKA_LIMS_FUNCTIONAL_TESTING
    return suite
