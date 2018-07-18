# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.tests.base import DataTestCase
from bika.lims.utils import tmpID
from bika.lims.utils.analysis import create_analysis
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, setRoles
from Products.CMFPlone.utils import _createObjectByType

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestMultiVerificationType(DataTestCase):
    """In Bika Setup, When Multi verification is enabled, one of 3 types of
    Multi Verification option should be chosen. Functional Testing of this new
    feature.
    """

    def setUp(self):
        super(TestMultiVerificationType, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ['Member', 'LabManager'])
        login(self.portal, TEST_USER_NAME)

    def tearDown(self):
        super(TestMultiVerificationType, self).tearDown()

    def test_MultiVerificationType(self):
        bika_setup = self.portal.bika_setup

        # Testing when the same user can verify multiple times
        bika_setup.setNumberOfRequiredVerifications(4)
        bika_setup.setTypeOfmultiVerification('self_multi_enabled')

        client = self.portal.clients['client-1']
        ar = _createObjectByType("AnalysisRequest", client, tmpID())
        servs = bika_setup.bika_analysisservices
        service = servs['analysisservice-3']
        service.setSelfVerification(True)
        an = create_analysis(ar, service)
        member = self.portal.portal_membership.getMemberById('admin')
        an.setVerificators(member.getUserName())
        an.setNumberOfRequiredVerifications(4)
        self.assertEquals(an.isUserAllowedToVerify(member), True)

        # Testing when the same user can verify multiple times but not
        # consequetively
        bika_setup.setTypeOfmultiVerification('self_multi_not_cons')
        self.assertEquals(an.isUserAllowedToVerify(member), False)

        # Testing when the same user can not verify more than once
        bika_setup.setTypeOfmultiVerification('self_multi_disabled')
        self.assertEquals(an.isUserAllowedToVerify(member), False)

        an.addVerificator(TEST_USER_NAME)
        bika_setup.setTypeOfmultiVerification('self_multi_not_cons')
        self.assertEquals(an.isUserAllowedToVerify(member), True)

        bika_setup.setTypeOfmultiVerification('self_multi_disabled')
        self.assertEquals(an.isUserAllowedToVerify(member), False)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMultiVerificationType))
    return suite
