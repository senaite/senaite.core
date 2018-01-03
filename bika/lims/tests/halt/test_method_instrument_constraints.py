# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login, logout

from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils.analysis import get_method_instrument_constraints
from bika.lims.utils.analysisrequest import create_analysisrequest

try:
    import unittest2 as unittest
except ImportError: # Python 2.7
    import unittest


class Test_MethodInstrumentConstraints(BikaFunctionalTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(Test_MethodInstrumentConstraints, self).setUp()
        login(self.portal, TEST_USER_NAME)

        # method-9: Protein Spectroscopy
        # analysis-service-3: Calcium (Ca)
        # instrument-10: Protein analyser
        self.method = self.portal.methods['method-9']
        self.method2 = self.portal.methods['method-10']
        self.service = self.portal.bika_setup.bika_analysisservices['analysisservice-3']
        self.instrument1 = self.portal.bika_setup.bika_instruments['instrument-10']
        self.instrument2 = self.portal.bika_setup.bika_instruments['instrument-11']
        self.instrument3 = self.portal.bika_setup.bika_instruments['instrument-3']
        self.servicemeor = self.service.getManualEntryOfResults()
        self.serviceieor = self.service.getInstrumentEntryOfResults()
        self.servicemeth = self.service.getMethods()
        self.i1method = self.instrument1.getMethod()
        self.i2method = self.instrument2.getMethod()
        self.i3method = self.instrument3.getMethod()
        self.serviceinsts = self.service.getInstruments()
        self.serviceinst = self.service.getInstrument()
        self.i1certdate = self.instrument1.getCertifications()[0].getValidTo()
        self.i2certdate = self.instrument2.getCertifications()[0].getValidTo()
        self.i3certdate = self.instrument3.getCertifications()[0].getValidTo()
        self.instrument1.getCertifications()[0].setValidTo('3000-01-01')
        self.instrument2.getCertifications()[0].setValidTo('3000-01-01')
        self.instrument3.getCertifications()[0].setValidTo('3000-01-01')

    def tearDown(self):
        logout()
        self.service.setManualEntryOfResults(self.servicemeor)
        self.service.setInstrumentEntryOfResults(self.serviceieor)
        self.service.setMethods(self.servicemeth)
        self.instrument1.setMethod(self.i1method)
        self.instrument2.setMethod(self.i2method)
        self.instrument3.setMethod(self.i3method)
        self.instrument1.setDisposeUntilNextCalibrationTest(False)
        self.instrument2.setDisposeUntilNextCalibrationTest(False)
        self.instrument3.setDisposeUntilNextCalibrationTest(False)
        self.service.setInstruments(self.serviceinsts)
        self.service.setInstrument(self.serviceinst)
        self.instrument1.getLatestValidCertification().setValidTo(self.i1certdate)
        self.instrument2.getLatestValidCertification().setValidTo(self.i2certdate)
        self.instrument3.getLatestValidCertification().setValidTo(self.i3certdate)
        super(Test_MethodInstrumentConstraints, self).tearDown()

    def test_RegularAnalyses(self):
        """
            See docs/imm_results_entry_behaviour.png for further details
        """

        # Basic simulation
        # B1
        rule = 'YYYYYYYY'
        output = [1, 1, 1, 1, 1]
        self.service.setInstrumentEntryOfResults(True)
        self.service.setManualEntryOfResults(True)
        self.service.setMethods([self.method])
        self.instrument1.setMethod(self.method)
        self.instrument2.setMethod(self.method)
        self.instrument1.setDisposeUntilNextCalibrationTest(False)
        self.instrument2.setDisposeUntilNextCalibrationTest(False)
        self.service.setInstruments([self.instrument1, self.instrument2])
        self.service.setInstrument(self.instrument1)
        self.assertTrue(self.service.getManualEntryOfResults())
        self.assertTrue(self.service.getInstrumentEntryOfResults())
        self.assertTrue(self.instrument1.getMethod().UID(), self.method.UID())
        self.assertTrue(self.instrument2.getMethod().UID(), self.method.UID())
        self.assertFalse(self.instrument1.getDisposeUntilNextCalibrationTest())
        self.assertFalse(self.instrument2.getDisposeUntilNextCalibrationTest())
        self.assertTrue(len(self.service.getAvailableInstruments()) == 2)
        self.assertTrue(self.instrument1 in self.service.getAvailableInstruments())
        self.assertTrue(self.instrument2 in self.service.getAvailableInstruments())
        self.assertEqual(self.service.getInstrument().UID(), self.instrument1.UID())
        self.assertTrue(len(self.service.getMethods()) == 1)
        self.assertEqual(self.service.getMethods()[0].UID(), self.method.UID())
        ar = self.create_ar(self.service)
        auids = [ar.getAnalyses()[0].UID]
        constraint = get_method_instrument_constraints(ar, auids)[auids[0]]
        cons = constraint.get(self.method.UID(), None)
        self.assertFalse(cons is None)
        trimmed = cons[10][1:len(rule)+1]
        self.assertEqual(trimmed, rule)
        self.assertEqual(cons[0], output[0])  # Method list visible?
        self.assertEqual(cons[1], output[1])  # None in methods list?
        self.assertEqual(cons[2], output[2])  # Instrument list visible?
        self.assertEqual(cons[3], output[3])  # None in instruments list?
        self.assertEqual(cons[5], output[4])  # Results field editable

        # Automatic simulation
        conds = {
            'YYYYYYYY':  [1, 1, 1, 1, 1, 0],  # B1
            'YYYYYYNYY': [1, 1, 1, 1, 1, 1],  # B3
            'YYYYYYNYN': [1, 1, 1, 1, 1, 1],  # B4
            'YYYYYN':    [1, 1, 1, 1, 1, 1],  # B6
            'YYYYN':     [1, 1, 1, 1, 1, 0],  # B7
            'YYYNYYYY':  [1, 1, 1, 0, 1, 0],  # B8
            'YYYNYYNYY': [1, 1, 1, 0, 1, 1],  # B10
            'YYYNYYNYN': [1, 1, 1, 1, 0, 1],  # B11
            'YYYNYN':    [1, 1, 1, 1, 0, 1],  # B13
            'YYNYYYYY':  [1, 1, 1, 1, 1, 0],  # B15
            'YYNYYYNYY': [1, 1, 1, 1, 1, 1],  # B17
            'YYNYYYNYN': [1, 1, 1, 1, 1, 1],  # B18
            'YYNYYN':    [1, 1, 1, 1, 1, 1],  # B20
            'YYNYN':     [1, 1, 1, 1, 1, 0],  # B21
            'YNY':       [2, 0, 0, 0, 1, 0],  # B22
            'YNN':       [0, 0, 0, 0, 1, 0],  # B23
            'NYYYYYYY':  [3, 2, 1, 1, 1, 0],  # B24
            'NYYYYYNYY': [3, 2, 1, 1, 1, 1],  # B26
            'NYYYYYNYN': [3, 2, 1, 1, 1, 1],  # B27
            'NYYYYN':    [3, 2, 1, 1, 1, 1],  # B29
            'NYYNYYYY':  [3, 2, 1, 0, 1, 0],  # B31
            'NYYNYYNYY': [3, 2, 1, 0, 1, 1],  # B33
            'NYYNYYNYN': [3, 2, 1, 1, 0, 1],  # B34
            'NYYNYN':    [3, 2, 1, 1, 0, 1],  # B36
            'NYNYYYYY':  [3, 1, 1, 0, 1, 0],  # B38
            'NYNYYYNYY': [3, 1, 1, 0, 1, 1],  # B40
            'NYNYYYNYN': [3, 1, 1, 1, 0, 1],  # B41
            'NYNYYN':    [3, 1, 1, 0, 0, 1],  # B43
            'NYNYN':     [3, 1, 1, 0, 0, 1],  # B44"

            # Situations that cannot be simulated
            # 'YYYYYYYN':  [1, 1, 1, 1, 1, 0],  # B2 -- IMPOSSIBLE
            # 'YYYYYYNN':  [1, 1, 1, 1, 1, 1],  # B5 -- IMPOSSIBLE
            # 'YYYNYYYN':  [1, 1, 1, 0, 1, 0],  # B9 -- IMPOSSIBLE
            # 'YYYNYYNN':  [1, 1, 1, 0, 1, 1],  # B12 -- IMPOSSIBLE
            # 'YYYNN':     [1, 1, 1, 1, 0, 1],  # B14 -- CANNOT REPRODUCE
            # 'YYNYYYYN':  [1, 1, 1, 1, 1, 0],  # B16 -- IMPOSSIBLE
            # 'YYNYYYNN':  [1, 1, 1, 1, 1, 1],  # B19 -- IMPOSSIBLE
            # 'NYYYYYYN':  [3, 2, 1, 1, 1, 0],  # B25 -- IMPOSSIBLE
            # 'NYYYYYNN':  [3, 2, 1, 1, 1, 1],  # B28 -- IMPOSSIBLE
            # 'NYYYN':     [3, 2, 1, 1, 0, 1],  # B30 -- CANNOT REPRODUCE
            # 'NYYNYYYN':  [3, 2, 1, 0, 1, 0],  # B32 -- IMPOSSIBLE
            # 'NYYNYYNN':  [3, 2, 1, 0, 1, 1],  # B35 -- IMPOSSIBLE
            # 'NYYNN':     [3, 2, 1, 1, 0, 1],  # B37 -- CANNOT REPRODUCE
            # 'NYNYYYYN':  [3, 1, 1, 0, 1, 0],  # B39 -- IMPOSSIBLE
            # 'NYNYYYNN':  [3, 1, 1, 0, 1, 1],  # B42 -- IMPOSSIBLE
        }

        for k, v in conds.items():
            # Analysis allows instrument entry?
            a_instruentry = len(k) > 1 and k[1] == 'Y'
            # Analysis allows manual entry?
            a_manualentry = k[0] == 'Y' or not a_instruentry
            # Method is not None?
            m_isnotnone = len(k) > 2 and k[2] == 'Y'
            # Method allows manual entry?
            m_manualentry = (len(k) > 3 and k[3] == 'Y')
            # At least one instrument available?
            m_instravilab = len(k) > 4 and k[4] == 'Y'
            # All instruments valid?
            m_allinstrval = len(k) > 6 and k[6] == 'Y'
            # Valid instruments available?
            m_validinstru = (len(k) > 5 and k[5] == 'Y') or (m_allinstrval)
            # Method allows the ASs default instr?
            m_allowsdefin = len(k) > 7 and k[7] == 'Y'
            # Default instrument is valid?
            i_definstrval = (len(k) > 8 and k[8] == 'Y') or (m_allowsdefin and m_allinstrval)
            defmeth = self.method

            if a_manualentry:
                self.service.setManualEntryOfResults(True)
                self.service.setMethods([self.method, self.method2])
                self.service.setInstrumentEntryOfResults(a_instruentry)
                self.assertTrue(self.service.getManualEntryOfResults())
                self.assertEqual(self.service.getInstrumentEntryOfResults(),
                                 a_instruentry)
            else:
                self.service.setInstrumentEntryOfResults(True)
                self.service.setManualEntryOfResults(False)
                self.service.setMethods([])
                self.assertTrue(self.service.getInstrumentEntryOfResults())
                self.assertFalse(self.service.getManualEntryOfResults())

            self.method.setManualEntryOfResults(m_manualentry)
            self.assertEqual(self.method.getManualEntryOfResults(), m_manualentry)

            if m_instravilab:
                if m_isnotnone:
                    self.instrument1.setMethod(self.method)
                    self.instrument2.setMethod(self.method)
                    self.instrument3.setMethod(self.method2)
                    self.assertTrue(self.instrument1.getMethod().UID(), self.method.UID())
                    self.assertTrue(self.instrument2.getMethod().UID(), self.method.UID())
                else:
                    self.instrument1.setMethod(None)
                    self.instrument2.setMethod(None)
                    self.instrument3.setMethod(None)
                self.service.setInstrument(self.instrument1)
                if m_validinstru:
                    if m_allinstrval:
                        self.instrument1.setDisposeUntilNextCalibrationTest(False)
                        self.instrument2.setDisposeUntilNextCalibrationTest(False)
                        self.assertFalse(self.instrument1.getDisposeUntilNextCalibrationTest())
                        self.assertFalse(self.instrument2.getDisposeUntilNextCalibrationTest())
                    else:
                        self.instrument1.setDisposeUntilNextCalibrationTest(False)
                        self.instrument2.setDisposeUntilNextCalibrationTest(True)
                        self.assertFalse(self.instrument1.getDisposeUntilNextCalibrationTest())
                        self.assertTrue(self.instrument2.getDisposeUntilNextCalibrationTest())

                    if m_allowsdefin:
                        self.service.setInstruments([self.instrument2, self.instrument1, self.instrument3])
                        if not i_definstrval:
                            self.instrument2.setDisposeUntilNextCalibrationTest(True)
                            self.service.setInstruments([self.instrument2, self.instrument1, self.instrument3])
                            self.service.setInstrument(self.instrument2)
                    else:
                        self.service.setInstruments([self.instrument3])
                else:
                    self.instrument1.setDisposeUntilNextCalibrationTest(True)
                    self.assertTrue(self.instrument1.getDisposeUntilNextCalibrationTest())
                    self.instrument2.setDisposeUntilNextCalibrationTest(True)
                    self.assertTrue(self.instrument2.getDisposeUntilNextCalibrationTest())
                    self.service.setInstruments([self.instrument1])
            else:
                self.instrument1.setMethod(None)
                self.instrument2.setMethod(None)
                self.instrument1.setDisposeUntilNextCalibrationTest(False)
                self.instrument1.setDisposeUntilNextCalibrationTest(False)
                self.service.setInstruments([])
                self.service.setInstrument(None)

            # Create the AR
            client = self.portal.clients['client-1']
            sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
            values = {'Client': client.UID(),
                      'Contact': client.getContacts()[0].UID(),
                      'SamplingDate': '2016-01-01',
                      'SampleType': sampletype.UID()}
            request = {}
            services = [self.service,]
            ar = create_analysisrequest(client, request, values, services)
            wf = getToolByName(ar, 'portal_workflow')
            wf.doActionFor(ar, 'receive')

            # Get the constraints
            auids = [ar.getAnalyses()[0].UID]
            constraint = get_method_instrument_constraints(ar, auids)[auids[0]]

            muid = self.method.UID() if m_isnotnone else ''
            cons = constraint.get(muid, None)
            self.assertFalse(cons is None)
            trimmed = cons[10][1:len(k)+1]
            self.assertTrue(trimmed.startswith(k))
            self.assertEqual(cons[0], v[0])  # Method list visible?
            self.assertEqual(cons[1], v[1])  # None in methods list?
            self.assertEqual(cons[2], v[2])  # Instrument list visible?
            self.assertEqual(cons[3], v[3])  # None in instruments list?
            self.assertEqual(cons[5], v[4])  # Results field editable
            self.assertEqual(cons[6] == '', v[5] == 0)  # Error message?

            '''
            if cons:
                trimmed = cons[10][1:len(k)+1]
                if not trimmed.startswith(k):
                    print '[%s] %s' % ('OK' if trimmed.startswith(k) else 'KO', k)
                    print '     %s' % trimmed
            '''

    def create_ar(self, analysisservice):
        # Create the AR
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2016-01-01',
                  'SampleType': sampletype.UID()}
        request = {}
        services = [analysisservice,]
        ar = create_analysisrequest(client, request, values, services)
        wf = getToolByName(ar, 'portal_workflow')
        wf.doActionFor(ar, 'receive')
        return ar
