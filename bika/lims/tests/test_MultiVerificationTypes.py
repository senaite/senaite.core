# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.


from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from bika.lims.utils import tmpID
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.utils.analysisrequest import create_analysisrequest

import unittest

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class Test_MultiVerificationType(BikaFunctionalTestCase):
    """
    In Bika Setup, When Multi verification is enabled, one of 3 types of Multi Verification
    option should be chosen. Functional Testing of this new feature.
    """
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(Test_MultiVerificationType, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def tearDown(self):
        logout()
        super(Test_MultiVerificationType, self).tearDown()

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
        an = _createObjectByType('Analysis', ar, tmpID())
        member = self.portal.portal_membership.getMemberById('admin')
        an.setService(service)
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
    suite.addTest(unittest.makeSuite(Test_MultiVerificationType))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
