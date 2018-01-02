# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import logger
from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils.analysisrequest import create_analysisrequest
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from plone import api
import unittest

try:
    import unittest2 as unittest
except ImportError: # Python 2.7
    import unittest


class LIMS2257(BikaFunctionalTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(LIMS2257, self).setUp()
        login(self.portal, TEST_USER_NAME)
        servs = self.portal.bika_setup.bika_analysisservices
        self.services = [servs['analysisservice-3'],
                         servs['analysisservice-6'],
                         servs['analysisservice-7']]
        # Enabling the workflow
        self.portal.bika_setup.setSamplingWorkflowEnabled(True)
        self.portal.bika_setup.setScheduleSamplingEnabled(True)

    def tearDown(self):
        # Enabling the workflow
        self.portal.bika_setup.setSamplingWorkflowEnabled(False)
        self.portal.bika_setup.setScheduleSamplingEnabled(False)
        logout()
        super(LIMS2257, self).tearDown()

    def test_group_samplingcoordinators_exist(self):
        """
        Testing if the SamplingCoordinators group does exist
        """
        portal_groups = self.portal.portal_groups
        self.assertIn('SamplingCoordinators', portal_groups.listGroupIds())

    def test_sample_workflow_action_schedule_sampling(self):
        """
        This test validates the function
        bika/lims//browser/analysisrequest/workflow.py/workflow_action_schedule_sampling
        """
        from bika.lims.utils.workflow import schedulesampling
        workflow = getToolByName(self.portal, 'portal_workflow')
        pc = getToolByName(self.portal, 'portal_catalog')
        sampler = api.user.get(username='sampler1')
        coordinator = self.createUser('SamplingCoordinator', 'cord1')
        # checking if the user belongs to the coordinators group
        mtool = getToolByName(self.portal, 'portal_membership')
        groups_tool = getToolByName(self.portal, 'portal_groups')
        usr_groups = groups_tool.getGroupsByUserId('cord1')
        self.assertIn(
            'SamplingCoordinators', [group.id for group in usr_groups])
        # Getting the client
        client = self.portal.clients['client-1']
        # Getting a sample type
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        # Creating an AR
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        request = {}
        services = [s.UID() for s in self.services]
        # creating the analysisrequest
        ar = create_analysisrequest(client, request, values, services)
        self.assertEqual(
            workflow.getInfoFor(ar, 'review_state'), 'to_be_sampled')
        # Changing user to coordinator
        logout()
        login(self.portal, 'cord1')
        # If ScheduledSamplingSampler is empty and ScheduleSamplingEnabled,
        # no workflow_action_schedule_sampling can be done
        schedulesampling.doTransition(ar.getSample())
        self.assertEqual(
            workflow.getInfoFor(ar, 'review_state'), 'to_be_sampled')
        self.assertEqual(
            workflow.getInfoFor(ar.getSample(), 'review_state'),
            'to_be_sampled')
        # set a value in ScheduledSamplingSampler
        ar.setScheduledSamplingSampler(sampler)
        schedulesampling.doTransition(ar.getSample())
        self.assertEqual(
            workflow.getInfoFor(ar, 'review_state'), 'scheduled_sampling')
        self.assertEqual(
            workflow.getInfoFor(ar.getSample(), 'review_state'),
            'scheduled_sampling')

    def createUser(self, role, username='test_1'):
        #workflow.getTransitionsFor(ar.getSample())
        member = self.portal.portal_registration.addMember(
            username,
            username,
            properties={
                'username': 'username',
                'email': username + "@example.com",
                'fullname': username}
        )
        # Add user to all specified groups
        group_id = role + "s"
        # Add user to all specified roles
        self.portal.portal_groups.addPrincipalToGroup(
            member.getUserName(), group_id)
        return member


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LIMS2257))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
