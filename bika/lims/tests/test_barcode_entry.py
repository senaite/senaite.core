# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json

import transaction
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

from bika.lims.barcode import barcode_entry
from bika.lims.testing import BIKA_LIMS_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils import tmpID, changeWorkflowState
from bika.lims.workflow import doActionFor

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


class TestBarcodeEntry(BikaFunctionalTestCase):
    layer = BIKA_LIMS_FUNCTIONAL_TESTING

    def addthing(self, folder, portal_type, **kwargs):
        thing = _createObjectByType(portal_type, folder, tmpID())
        thing.unmarkCreationFlag()
        thing.edit(**kwargs)
        thing._renameAfterCreation()
        return thing

    def setUp(self):
        super(TestBarcodeEntry, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ['Member', 'LabManager'])
        login(self.portal, TEST_USER_NAME)
        clients = self.portal.clients
        bs = self.portal.bika_setup
        # @formatter:off
        self.client = self.addthing(clients, 'Client', title='Happy Hills', ClientID='HH')
        contact = self.addthing(self.client, 'Contact', Firstname='Rita', Lastname='Mohale')
        container = self.addthing(bs.bika_containers, 'Container', title='Bottle', capacity="10ml")
        sampletype = self.addthing(bs.bika_sampletypes, 'SampleType', title='Water', Prefix='H2O')
        samplepoint = self.addthing(bs.bika_samplepoints, 'SamplePoint', title='Toilet')
        service = self.addthing(bs.bika_analysisservices, 'AnalysisService', title='Ecoli', Keyword="ECO")
        batch = self.addthing(self.portal.batches, 'Batch', title='B1')
        # Create Sample with single partition
        self.sample1 = self.addthing(self.client, 'Sample', SampleType=sampletype)
        self.sample2 = self.addthing(self.client, 'Sample', SampleType=sampletype)
        self.addthing(self.sample1, 'SamplePartition', Container=container)
        self.addthing(self.sample2, 'SamplePartition', Container=container)
        # Create an AR
        self.ar1 = self.addthing(self.client, 'AnalysisRequest', Contact=contact,
                                Sample=self.sample1, Analyses=[service], SamplingDate=DateTime())
        # Create a secondary AR - linked to a Batch
        self.ar2 = self.addthing(self.client, 'AnalysisRequest', Contact=contact,
                                Sample=self.sample1, Analyses=[service], SamplingDate=DateTime(),
                                Batch=batch)
        # Create an AR - single AR on sample2
        self.ar3 = self.addthing(self.client, 'AnalysisRequest', Contact=contact,
                                Sample=self.sample2, Analyses=[service], SamplingDate=DateTime())
        # @formatter:on
        wf = getToolByName(self.portal, 'portal_workflow')
        for ar in self.ar1, self.ar2, self.ar3:
            # Set initial AR state
            doActionFor(ar, 'no_sampling_workflow')

        transaction.commit()

    def tearDown(self):
        super(TestBarcodeEntry, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def test_ar_states_without_batch(self):
        wf = getToolByName(self.portal, 'portal_workflow')
        self.portal.REQUEST['entry'] = self.ar1.id
        self.portal.REQUEST['_authenticator'] = self.getAuthenticator()

        value = json.loads(barcode_entry(self.portal, self.portal.REQUEST)())
        if value.get('failure', False):
            self.fail('failure code in json return: ' + value['error'])
        state = wf.getInfoFor(self.ar1, 'review_state')
        self.assertTrue(state == 'sample_received',
                        'AR is in %s state; should be sample_received' % state)

        value = json.loads(barcode_entry(self.portal, self.portal.REQUEST)())
        if value.get('failure', False):
            self.fail('failure code in json return: ' + value['error'])
        expected = self.ar1.absolute_url() + "/manage_results"
        self.assertEqual(value['url'], expected,
                         "AR redirect should be  %s but it's %s" % (
                             expected, value['url']))

        changeWorkflowState(self.ar1, 'bika_ar_workflow', 'verified')
        wf.getWorkflowById('bika_ar_workflow').updateRoleMappingsFor(self.ar1)
        self.ar1.reindexObject(idxs=['allowedRolesAndUsers'])

        value = json.loads(barcode_entry(self.portal, self.portal.REQUEST)())
        if value.get('failure', False):
            self.fail('failure code in json return: ' + value['error'])
        expected = self.ar1.absolute_url()
        self.assertEqual(value['url'], expected,
                         "AR redirect should be  %s but it's %s" % (
                             expected, value['url']))

    def test_batchbook_view(self):
        self.portal.REQUEST['entry'] = self.ar2.id
        self.portal.REQUEST['_authenticator'] = self.getAuthenticator()
        value = json.loads(barcode_entry(self.portal, self.portal.REQUEST)())
        expected = self.ar2.getBatch().absolute_url() + "/batchbook"
        err_msg = value['error'] if hasattr(value, 'error') else 'No error'
        self.assertEqual(value['failure'], False, err_msg)
        self.assertEqual(value['url'], expected,
                         "AR redirect should be batchbook %s but it's %s" % (
                             expected, value['url']))

    def test_sample_with_multiple_ars_redirects_to_self(self):
        self.portal.REQUEST['entry'] = self.sample1.id
        self.portal.REQUEST['_authenticator'] = self.getAuthenticator()
        value = json.loads(barcode_entry(self.portal, self.portal.REQUEST)())
        expected = self.sample1.absolute_url()
        self.assertEqual(value['url'], expected,
                         "sample1 redirect should be self:%s but it's %s" % (
                             expected, value['url']))


def test_sample_with_single_ar_redirects_to_AR(self):
    self.portal.REQUEST['entry'] = self.sample2.id
    self.portal.REQUEST['_authenticator'] = self.getAuthenticator()
    value = json.loads(barcode_entry(self.portal, self.portal.REQUEST)())
    expected = self.ar3.absolute_url()
    self.assertEqual(value['url'], expected,
                     "sample2 redirect should be ar3:%s but it's %s" % (
                         expected, value['url']))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBarcodeEntry))
    suite.layer = BIKA_LIMS_FUNCTIONAL_TESTING
    return suite
