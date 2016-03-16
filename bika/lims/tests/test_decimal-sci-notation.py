# -*- coding: utf-8 -*-

from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils.analysisrequest import create_analysisrequest
from bika.lims.workflow import doActionFor
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
import unittest

try:
    import unittest2 as unittest
except ImportError: # Python 2.7
    import unittest


class Test_DecimalSciNotation(BikaFunctionalTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(Test_DecimalSciNotation, self).setUp()
        login(self.portal, TEST_USER_NAME)

        # analysis-service-3: Calcium (Ca)
        servs = self.portal.bika_setup.bika_analysisservices
        self.service = servs['analysisservice-3']

        # Original values
        self.orig_as_prec = self.service.getPrecision()
        self.orig_as_expf = self.service.getExponentialFormatPrecision()
        self.orig_as_ldl  = self.service.getLowerDetectionLimit()
        self.orig_bs_expf = self.service.getExponentialFormatThreshold()
        self.orig_bs_scin = self.service.getScientificNotationResults()

    def tearDown(self):
        self.portal.bika_setup.setExponentialFormatThreshold(self.orig_bs_expf)
        self.portal.bika_setup.setScientificNotationResults(self.orig_bs_scin)
        self.service.setPrecision(self.orig_as_prec)
        self.service.setExponentialFormatPrecision(self.orig_as_expf)
        self.service.setLowerDetectionLimit(self.orig_as_ldl)
        logout()
        super(Test_DecimalSciNotation, self).tearDown()

    def test_DecimalSciNotation(self):
        # Notations
        # '1' => aE+b / aE-b
        # '2' => ax10^b / ax10^-b
        # '3' => ax10^b / ax10^-b (with superscript)
        # '4' => a·10^b / a·10^-b
        # '5' => a·10^b / a·10^-b (with superscript)
        matrix = [
            # as_prec  as_exp  not  result    formatted result
            # -------  ------  ---  --------  -------------------------------
            [0,        0,      1, '0',            '0'],
            [0,        0,      2, '0',            '0'],
            [0,        0,      3, '0',            '0'],
            [0,        0,      4, '0',            '0'],
            [0,        0,      5, '0',            '0'],
            [0,        5,      1, '0.00001',      '1e-05'],
            [0,        5,      2, '0.00001',      '1x10^-5'],
            [0,        5,      3, '0.00001',      '1x10<sup>-5</sup>'],
            [0,        5,      4, '0.00001',      '1·10^-5'],
            [0,        5,      5, '0.00001',      '1·10<sup>-5</sup>'],
            [0,        5,      1, '-0.00001',     '-1e-05'],
            [0,        5,      2, '-0.00001',     '-1x10^-5'],
            [0,        5,      3, '-0.00001',     '-1x10<sup>-5</sup>'],
            [0,        5,      4, '-0.00001',     '-1·10^-5'],
            [0,        5,      5, '-0.00001',     '-1·10<sup>-5</sup>'],
            [2,        0,      1, '0',            '0.00'],
            [2,        0,      2, '0',            '0.00'],
            [2,        0,      3, '0',            '0.00'],
            [2,        0,      4, '0',            '0.00'],
            [2,        0,      5, '0',            '0.00'],
            [2,        1,      1, '0',            '0.00'],
            [2,        1,      2, '0',            '0.00'],
            [2,        1,      3, '0',            '0.00'],
            [2,        1,      4, '0',            '0.00'],
            [2,        1,      5, '0',            '0.00'],
            [2,        5,      1, '0.01',         '0.01'],
            [2,        5,      2, '0.01',         '0.01'],
            [2,        5,      3, '0.01',         '0.01'],
            [2,        5,      4, '0.01',         '0.01'],
            [2,        5,      5, '0.01',         '0.01'],
            [2,        5,      1, '0.00012',      '0.00'],
            [2,        5,      2, '0.00012',      '0.00'],
            [2,        5,      3, '0.00012',      '0.00'],
            [2,        5,      4, '0.00012',      '0.00'],
            [2,        5,      5, '0.00012',      '0.00'],
            [2,        5,      1, '0.00001',      '1e-05'],
            [2,        5,      2, '0.00001',      '1x10^-5'],
            [2,        5,      3, '0.00001',      '1x10<sup>-5</sup>'],
            [2,        5,      4, '0.00001',      '1·10^-5'],
            [2,        5,      5, '0.00001',      '1·10<sup>-5</sup>'],
            [2,        5,      1, '0.0000123',    '1.23e-05'],
            [2,        5,      2, '0.0000123',    '1.23x10^-5'],
            [2,        5,      3, '0.0000123',    '1.23x10<sup>-5</sup>'],
            [2,        5,      4, '0.0000123',    '1.23·10^-5'],
            [2,        5,      5, '0.0000123',    '1.23·10<sup>-5</sup>'],
            [2,        5,      1, '-0.00001',     '-1e-05'],
            [2,        5,      2, '-0.00001',     '-1x10^-5'],
            [2,        5,      3, '-0.00001',     '-1x10<sup>-5</sup>'],
            [2,        5,      4, '-0.00001',     '-1·10^-5'],
            [2,        5,      5, '-0.00001',     '-1·10<sup>-5</sup>'],
            [2,        5,      1, '-0.0000123',   '-1.23e-05'],
            [2,        5,      2, '-0.0000123',   '-1.23x10^-5'],
            [2,        5,      3, '-0.0000123',   '-1.23x10<sup>-5</sup>'],
            [2,        5,      4, '-0.0000123',   '-1.23·10^-5'],
            [2,        5,      5, '-0.0000123',   '-1.23·10<sup>-5</sup>'],
            [2,        5,      1, '1234',         '1234.00'],
            [2,        5,      2, '1234',         '1234.00'],
            [2,        5,      3, '1234',         '1234.00'],
            [2,        5,      4, '1234',         '1234.00'],
            [2,        5,      5, '1234',         '1234.00'],
            [2,        5,      1, '1234.01',      '1234.01'],
            [2,        5,      2, '1234.01',      '1234.01'],
            [2,        5,      3, '1234.01',      '1234.01'],
            [2,        5,      4, '1234.01',      '1234.01'],
            [2,        5,      5, '1234.01',      '1234.01'],
            [2,        5,      1, '1234.00001',   '1234.00'],
            [2,        5,      2, '1234.00001',   '1234.00'],
            [2,        5,      3, '1234.00001',   '1234.00'],
            [2,        5,      4, '1234.00001',   '1234.00'],
            [2,        5,      5, '1234.00001',   '1234.00'],
            [2,        5,      1, '1234.0000123', '1234.00'],
            [2,        5,      2, '1234.0000123', '1234.00'],
            [2,        5,      3, '1234.0000123', '1234.00'],
            [2,        5,      4, '1234.0000123', '1234.00'],
            [2,        5,      5, '1234.0000123', '1234.00'],
            [2,        5,      1, '-1234.00001',  '-1234.00'],
            [2,        5,      2, '-1234.00001',  '-1234.00'],
            [2,        5,      3, '-1234.00001',  '-1234.00'],
            [2,        5,      4, '-1234.00001',  '-1234.00'],
            [2,        5,      5, '-1234.00001',  '-1234.00'],
            [2,        5,      1, '-1234.0000123','-1234.00'],
            [2,        5,      2, '-1234.0000123','-1234.00'],
            [2,        5,      3, '-1234.0000123','-1234.00'],
            [2,        5,      4, '-1234.0000123','-1234.00'],
            [2,        5,      5, '-1234.0000123','-1234.00'],
            [2,        -6,      1, '12340',       '1.234e04'],
            [2,        -4,      1, '12340',       '1.234e04'],
            [2,        -4,      2, '12340',       '1.234x10^4'],
            [2,        -4,      3, '12340',       '1.234x10<sup>4</sup>'],
            [2,        -4,      4, '12340',       '1.234·10^4'],
            [2,        -4,      5, '12340',       '1.234·10<sup>4</sup>'],
            [2,        -4,      1, '12340.01',    '1.234001e04'],
            [2,        -4,      2, '12340.01',    '1.234001x10^4'],
            [2,        -4,      3, '12340.01',    '1.234001x10<sup>4</sup>'],
            [2,        -4,      4, '12340.01',    '1.234001·10^4'],
            [2,        -4,      5, '12340.01',    '1.234001·10<sup>4</sup>'],
            [2,        -6,      1, '-12340',      '-1.234e04'],
            [2,        -4,      1, '-12340',      '-1.234e04'],
            [2,        -4,      2, '-12340',      '-1.234x10^4'],
            [2,        -4,      3, '-12340',      '-1.234x10<sup>4</sup>'],
            [2,        -4,      4, '-12340',      '-1.234·10^4'],
            [2,        -4,      5, '-12340',      '-1.234·10<sup>4</sup>'],
            [2,        -4,      1, '-12340.01',   '-1.234001e04'],
            [2,        -4,      2, '-12340.01',   '-1.234001x10^4'],
            [2,        -4,      3, '-12340.01',   '-1.234001x10<sup>4</sup>'],
            [2,        -4,      4, '-12340.01',   '-1.234001·10^4'],
            [2,        -4,      5, '-12340.01',   '-1.234001·10<sup>4</sup>'],
        ]
        s = self.service
        s.setLowerDetectionLimit('-99999') # We want to test results below 0 too
        prevm = []
        an = None
        bs = self.portal.bika_setup;
        for m in matrix:
            # Create the AR and set the values to the AS, but only if necessary
            if not an or prevm[0] != m[0] or prevm[1] != m[1]:
                s.setPrecision(m[0])
                s.setExponentialFormatPrecision(m[1])
                self.assertEqual(s.getPrecision(), m[0])
                self.assertEqual(s.Schema().getField('Precision').get(s), m[0])
                self.assertEqual(s.getExponentialFormatPrecision(), m[1])
                self.assertEqual(s.Schema().getField('ExponentialFormatPrecision').get(s), m[1])
                client = self.portal.clients['client-1']
                sampletype = bs.bika_sampletypes['sampletype-1']
                values = {'Client': client.UID(),
                          'Contact': client.getContacts()[0].UID(),
                          'SamplingDate': '2015-01-01',
                          'SampleType': sampletype.UID()}
                ar = create_analysisrequest(client, {}, values, [s.UID()])
                wf = getToolByName(ar, 'portal_workflow')
                wf.doActionFor(ar, 'receive')
                an = ar.getAnalyses()[0].getObject()
                prevm = m;
            an.setResult(m[3])

            self.assertEqual(an.getResult(), m[3])
            self.assertEqual(an.Schema().getField('Result').get(an), m[3])
            fr = an.getFormattedResult(sciformat=m[2])
            #print '%s   %s   %s   %s  =>  \'%s\' ?= \'%s\'' % (m[0],m[1],m[2],m[3],m[4],fr)
            self.assertEqual(fr, m[4])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_DecimalSciNotation))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
