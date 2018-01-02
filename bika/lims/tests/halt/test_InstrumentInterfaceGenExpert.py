# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import codecs
import traceback

import transaction
from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login, logout

from bika.lims.browser.resultsimport.resultsimport import ConvertToUploadFile
from bika.lims.exportimport import instruments
from bika.lims.exportimport.instruments.genexpert.genexpert \
    import GeneXpertParser, GeneXpertImporter
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils.analysisrequest import create_analysisrequest

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class Test_InstrumentInterfaceGeneXpert(BikaFunctionalTestCase):
    """
    Tests of GeneXpert Interface import.
    """
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(Test_InstrumentInterfaceGeneXpert, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def tearDown(self):
        logout()
        super(Test_InstrumentInterfaceGeneXpert, self).tearDown()

    def test_InstrumentInterfaceGeneXpert(self):

        # Checking if genexpert has already been added to Interface list.
        exims = []
        for exim_id in instruments.__all__:
            exims.append((exim_id))
        self.assertTrue('genexpert.genexpert' in exims)
        # Creating/ Getting some necessary objects.
        catalog = getToolByName(self.portal, 'portal_catalog')
        # Getting the first client
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID(),
                  'Profiles': ''
                  }
        # Getting some services
        services = catalog(portal_type = 'AnalysisService',
                            inactive_state = 'active')[:1]
        services[0].getObject().edit(Keyword="EbolaRUO")
        service_uids = [service.getObject().UID() for service in services]
        request = {}
        ar = create_analysisrequest(client, request, values, service_uids)
        wf = getToolByName(ar, 'portal_workflow')
        wf.doActionFor(ar, 'receive')

        # bsc = getToolByName(self.portal, 'bika_setup_catalog')
        # ins = bsc(portal_type='Instrument', inactive_state='active')
        transaction.commit()
        # Importing test file.
        import os
        dir_path = os.path.dirname(os.path.realpath(__file__))
        temp_file = codecs.open(dir_path+"/files/GeneXpert.csv",
                                encoding='utf-16-le')
        test_file = ConvertToUploadFile(temp_file)
        genex_parser = GeneXpertParser(test_file)
        importer = GeneXpertImporter(parser=genex_parser,
                                     context=self.portal,
                                     idsearchcriteria=['getId', 'getSampleID', 'getClientSampleID'],
                                     allowed_ar_states=['sample_received', 'attachment_due', 'to_be_verified'],
                                     allowed_analysis_states=None,
                                     override=[True, True])
        tbex = ''
        try:
            importer.process()
        except:
            tbex = traceback.format_exc()
        errors = importer.errors
        logs = importer.logs
        print logs
        print errors
        # TODO Add meaningful asserts!!!


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_InstrumentInterfaceGeneXpert))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
