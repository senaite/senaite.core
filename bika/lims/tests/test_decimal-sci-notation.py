# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims.tests.base import DataTestCase
from bika.lims.utils.analysisrequest import create_analysisrequest
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, setRoles
from Products.CMFCore.utils import getToolByName

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


class TestDecimalSciNotation(DataTestCase):

    def setUp(self):
        super(TestDecimalSciNotation, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ['Member', 'LabManager'])
        login(self.portal, TEST_USER_NAME)
        # analysis-service-3: Calcium (Ca)
        servs = self.portal.bika_setup.bika_analysisservices
        self.service = servs['analysisservice-3']

        # Original values
        self.orig_as_prec = self.service.getPrecision()
        self.orig_as_expf = self.service.getExponentialFormatPrecision()
        self.orig_as_ldl = self.service.getLowerDetectionLimit()
        self.orig_bs_expf = self.service.getExponentialFormatThreshold()
        self.orig_bs_scin = self.service.getScientificNotationResults()

    def tearDown(self):
        self.portal.bika_setup.setExponentialFormatThreshold(self.orig_bs_expf)
        self.portal.bika_setup.setScientificNotationResults(self.orig_bs_scin)
        self.service.setPrecision(self.orig_as_prec)
        self.service.setExponentialFormatPrecision(self.orig_as_expf)
        self.service.setLowerDetectionLimit(self.orig_as_ldl)
        super(TestDecimalSciNotation, self).tearDown()

    def test_DecimalSciNotation(self):
        # Notations
        # '1' => aE+b / aE-b
        # '2' => ax10^b / ax10^-b
        # '3' => ax10^b / ax10^-b (with superscript)
        # '4' => a·10^b / a·10^-b
        # '5' => a·10^b / a·10^-b (with superscript)
        matrix = [
            # as_prec  as_exp  not  result    formatted result
            # -------  ------  ---  --------  ------------------------------
            [0,        0,      1, '0',            '0'],
            [0,        0,      2, '0',            '0'],
            [0,        0,      3, '0',            '0'],
            [0,        0,      4, '0',            '0'],
            [0,        0,      5, '0',            '0'],

            # Crazy results!...
            # decimal precision << exponential precision, result << 1
            # For example:
            #   Precision=2, Exp precision=5 and result=0.000012
            #   Which is the less confusing result?
            #   a) 0.00
            #      Because the precision is 2 and the number of significant
            #      decimals is below precision.
            #   b) 1e-05
            #      Because the exponential precision is 5 and the number of
            #      significant decimals is equal or above the exp precision
            #
            # The best choice is (a): give priority to decimal precision
            # and omit the exponential precision.
            #
            # "Calculate precision from uncertainties" is the best antidote to
            # avoid these abnormal results, precisely... maybe the labmanager
            # setup the uncertainties ranges but missed to select the checkbox
            # "Calculate precision from uncertainties", so the system has to
            # deal with these incoherent values. From this point of view,
            # again the best choice is to give priority to decimal precision.
            #
            # We follow this rule:
            # if the result is >0 and <1 and the number of significant digits
            # is below the precision, ALWAYS use the decimal precision and don't
            # take exp precision into account
            [0,        5,      1, '0.00001',      '0'],
            [0,        5,      2, '0.00001',      '0'],
            [0,        5,      3, '0.00001',      '0'],
            [0,        5,      4, '0.00001',      '0'],
            [0,        5,      5, '0.00001',      '0'],
            [0,        5,      1, '-0.00001',     '0'],
            [0,        5,      2, '-0.00001',     '0'],
            [0,        5,      3, '-0.00001',     '0'],
            [0,        5,      4, '-0.00001',     '0'],
            [0,        5,      5, '-0.00001',     '0'],
            [2,        5,      1, '0.00012',      '0.00'],
            [2,        5,      2, '0.00012',      '0.00'],
            [2,        5,      3, '0.00012',      '0.00'],
            [2,        5,      4, '0.00012',      '0.00'],
            [2,        5,      5, '0.00012',      '0.00'],
            [2,        5,      1, '0.00001',      '0.00'],
            [2,        5,      2, '0.00001',      '0.00'],
            [2,        5,      3, '0.00001',      '0.00'],
            [2,        5,      4, '0.00001',      '0.00'],
            [2,        5,      5, '0.00001',      '0.00'],
            [2,        5,      1, '0.0000123',    '0.00'],
            [2,        5,      2, '0.0000123',    '0.00'],
            [2,        5,      3, '0.0000123',    '0.00'],
            [2,        5,      4, '0.0000123',    '0.00'],
            [2,        5,      5, '0.0000123',    '0.00'],
            [2,        5,      1, '0.01',         '0.01'],
            [2,        5,      2, '0.01',         '0.01'],
            [2,        5,      3, '0.01',         '0.01'],
            [2,        5,      4, '0.01',         '0.01'],
            [2,        5,      5, '0.01',         '0.01'],

            # More crazy results... exp_precision = 0 has no sense!
            # As above, the decimal precision gets priority
            [2,        0,      1, '0',            '0.00'],
            [2,        0,      2, '0',            '0.00'],
            [2,        0,      3, '0',            '0.00'],
            [2,        0,      4, '0',            '0.00'],
            [2,        0,      5, '0',            '0.00'],
            [2,        0,      1, '0.012',        '0.01'],
            [2,        0,      2, '0.012',        '0.01'],
            [2,        0,      3, '0.012',        '0.01'],
            [2,        0,      4, '0.012',        '0.01'],
            [2,        0,      5, '0.012',        '0.01'],

            [2,        1,      1, '0',            '0.00'],
            [2,        1,      2, '0',            '0.00'],
            [2,        1,      3, '0',            '0.00'],
            [2,        1,      4, '0',            '0.00'],
            [2,        1,      5, '0',            '0.00'],

            # Apply the sci notation here, but 'cut' the extra decimals first
            [2,        1,      1, '0.012',        '1e-02'],
            [2,        1,      2, '0.012',        '1x10^-2'],
            [2,        1,      3, '0.012',        '1x10<sup>-2</sup>'],
            [2,        1,      4, '0.012',        '1·10^-2'],
            [2,        1,      5, '0.012',        '1·10<sup>-2</sup>'],
            [2,        1,      1, '0.123',        '1.2e-01'],
            [2,        1,      2, '0.123',        '1.2x10^-1'],
            [2,        1,      3, '0.123',        '1.2x10<sup>-1</sup>'],
            [2,        1,      4, '0.123',        '1.2·10^-1'],
            [2,        1,      5, '0.123',        '1.2·10<sup>-1</sup>'],
            [2,        1,      1, '1.234',        '1.23'],
            [2,        1,      2, '1.234',        '1.23'],
            [2,        1,      3, '1.234',        '1.23'],
            [2,        1,      4, '1.234',        '1.23'],
            [2,        1,      5, '1.234',        '1.23'],
            [2,        1,      1, '12.345',       '1.235e01'],
            [2,        1,      2, '12.345',       '1.235x10^1'],
            [2,        1,      3, '12.345',       '1.235x10<sup>1</sup>'],
            [2,        1,      4, '12.345',       '1.235·10^1'],
            [2,        1,      5, '12.345',       '1.235·10<sup>1</sup>'],

            [4,        3,      1, '0.0000123',    '0.0000'],
            [4,        3,      2, '0.0000123',    '0.0000'],
            [4,        3,      3, '0.0000123',    '0.0000'],
            [4,        3,      4, '0.0000123',    '0.0000'],
            [4,        3,      5, '0.0000123',    '0.0000'],
            [4,        3,      1, '0.0001234',    '1e-04'],
            [4,        3,      2, '0.0001234',    '1x10^-4'],
            [4,        3,      3, '0.0001234',    '1x10<sup>-4</sup>'],
            [4,        3,      4, '0.0001234',    '1·10^-4'],
            [4,        3,      5, '0.0001234',    '1·10<sup>-4</sup>'],
            [4,        3,      1, '0.0012345',    '1.2e-03'],
            [4,        3,      2, '0.0012345',    '1.2x10^-3'],
            [4,        3,      3, '0.0012345',    '1.2x10<sup>-3</sup>'],
            [4,        3,      4, '0.0012345',    '1.2·10^-3'],
            [4,        3,      5, '0.0012345',    '1.2·10<sup>-3</sup>'],
            [4,        3,      1, '0.0123456',    '0.0123'],
            [4,        3,      1, '0.0123456',    '0.0123'],
            [4,        3,      2, '0.0123456',    '0.0123'],
            [4,        3,      3, '0.0123456',    '0.0123'],
            [4,        3,      4, '0.0123456',    '0.0123'],
            [4,        3,      5, '0.0123456',    '0.0123'],
            [4,        3,      1, '0.1234567',    '0.1235'],
            [4,        3,      2, '0.1234567',    '0.1235'],
            [4,        3,      3, '0.1234567',    '0.1235'],
            [4,        3,      4, '0.1234567',    '0.1235'],
            [4,        3,      5, '0.1234567',    '0.1235'],
            [4,        3,      1, '1.2345678',    '1.2346'],
            [4,        3,      2, '1.2345678',    '1.2346'],
            [4,        3,      3, '1.2345678',    '1.2346'],
            [4,        3,      4, '1.2345678',    '1.2346'],
            [4,        3,      5, '1.2345678',    '1.2346'],
            [4,        3,      1, '12.345678',    '12.3457'],
            [4,        3,      2, '12.345678',    '12.3457'],
            [4,        3,      3, '12.345678',    '12.3457'],
            [4,        3,      4, '12.345678',    '12.3457'],
            [4,        3,      5, '12.345678',    '12.3457'],
            [4,        3,      1, '123.45678',    '123.4568'],
            [4,        3,      2, '123.45678',    '123.4568'],
            [4,        3,      3, '123.45678',    '123.4568'],
            [4,        3,      4, '123.45678',    '123.4568'],
            [4,        3,      5, '123.45678',    '123.4568'],
            [4,        3,      1, '1234.5678',    '1.2345678e03'],
            [4,        3,      2, '1234.5678',    '1.2345678x10^3'],
            [4,        3,      3, '1234.5678',    '1.2345678x10<sup>3</sup>'],
            [4,        3,      4, '1234.5678',    '1.2345678·10^3'],
            [4,        3,      5, '1234.5678',    '1.2345678·10<sup>3</sup>'],

            [4,        3,      1, '-0.0000123',    '0.0000'],
            [4,        3,      2, '-0.0000123',    '0.0000'],
            [4,        3,      3, '-0.0000123',    '0.0000'],
            [4,        3,      4, '-0.0000123',    '0.0000'],
            [4,        3,      5, '-0.0000123',    '0.0000'],
            [4,        3,      1, '-0.0001234',    '-1e-04'],
            [4,        3,      2, '-0.0001234',    '-1x10^-4'],
            [4,        3,      3, '-0.0001234',    '-1x10<sup>-4</sup>'],
            [4,        3,      4, '-0.0001234',    '-1·10^-4'],
            [4,        3,      5, '-0.0001234',    '-1·10<sup>-4</sup>'],
            [4,        3,      1, '-0.0012345',    '-1.2e-03'],
            [4,        3,      2, '-0.0012345',    '-1.2x10^-3'],
            [4,        3,      3, '-0.0012345',    '-1.2x10<sup>-3</sup>'],
            [4,        3,      4, '-0.0012345',    '-1.2·10^-3'],
            [4,        3,      5, '-0.0012345',    '-1.2·10<sup>-3</sup>'],
            [4,        3,      1, '-0.0123456',    '-0.0123'],
            [4,        3,      1, '-0.0123456',    '-0.0123'],
            [4,        3,      2, '-0.0123456',    '-0.0123'],
            [4,        3,      3, '-0.0123456',    '-0.0123'],
            [4,        3,      4, '-0.0123456',    '-0.0123'],
            [4,        3,      5, '-0.0123456',    '-0.0123'],
            [4,        3,      1, '-0.1234567',    '-0.1235'],
            [4,        3,      2, '-0.1234567',    '-0.1235'],
            [4,        3,      3, '-0.1234567',    '-0.1235'],
            [4,        3,      4, '-0.1234567',    '-0.1235'],
            [4,        3,      5, '-0.1234567',    '-0.1235'],
            [4,        3,      1, '-1.2345678',    '-1.2346'],
            [4,        3,      2, '-1.2345678',    '-1.2346'],
            [4,        3,      3, '-1.2345678',    '-1.2346'],
            [4,        3,      4, '-1.2345678',    '-1.2346'],
            [4,        3,      5, '-1.2345678',    '-1.2346'],
            [4,        3,      1, '-12.345678',    '-12.3457'],
            [4,        3,      2, '-12.345678',    '-12.3457'],
            [4,        3,      3, '-12.345678',    '-12.3457'],
            [4,        3,      4, '-12.345678',    '-12.3457'],
            [4,        3,      5, '-12.345678',    '-12.3457'],
            [4,        3,      1, '-123.45678',    '-123.4568'],
            [4,        3,      2, '-123.45678',    '-123.4568'],
            [4,        3,      3, '-123.45678',    '-123.4568'],
            [4,        3,      4, '-123.45678',    '-123.4568'],
            [4,        3,      5, '-123.45678',    '-123.4568'],
            [4,        3,      1, '-1234.5678',    '-1.2345678e03'],
            [4,        3,      2, '-1234.5678',    '-1.2345678x10^3'],
            [4,        3,      3, '-1234.5678',    '-1.2345678x10<sup>3</sup>'],
            [4,        3,      4, '-1234.5678',    '-1.2345678·10^3'],
            [4,        3,      5, '-1234.5678',    '-1.2345678·10<sup>3</sup>'],

            [4,        3,      1, '1200000',      '1.2e06'],
            [4,        3,      2, '1200000',      '1.2x10^6'],
            [4,        3,      3, '1200000',      '1.2x10<sup>6</sup>'],
            [4,        3,      4, '1200000',      '1.2·10^6'],
            [4,        3,      5, '1200000',      '1.2·10<sup>6</sup>'],

            # Weird!!! negative values for exp precision
            [2,        -6,      1, '12340',       '12340.00'],
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
            [2,        -6,      1, '-12340',      '-12340.00'],
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

            [2,        6,       1, '12340',       '12340.00'],
            [2,        6,       2, '12340',       '12340.00'],
            [2,        6,       3, '12340',       '12340.00'],
            [2,        6,       4, '12340',       '12340.00'],
            [2,        6,       5, '12340',       '12340.00'],
            [2,        4,       1, '12340',       '1.234e04'],
            [2,        4,       2, '12340',       '1.234x10^4'],
            [2,        4,       3, '12340',       '1.234x10<sup>4</sup>'],
            [2,        4,       4, '12340',       '1.234·10^4'],
            [2,        4,       5, '12340',       '1.234·10<sup>4</sup>'],
            [2,        4,       1, '12340.0123',  '1.234001e04'],
            [2,        4,       2, '12340.0123',  '1.234001x10^4'],
            [2,        4,       3, '12340.0123',  '1.234001x10<sup>4</sup>'],
            [2,        4,       4, '12340.0123',  '1.234001·10^4'],
            [2,        4,       5, '12340.0123',  '1.234001·10<sup>4</sup>'],
            [2,        4,       1, '-12340',      '-1.234e04'],
            [2,        4,       2, '-12340',      '-1.234x10^4'],
            [2,        4,       3, '-12340',      '-1.234x10<sup>4</sup>'],
            [2,        4,       4, '-12340',      '-1.234·10^4'],
            [2,        4,       5, '-12340',      '-1.234·10<sup>4</sup>'],
            [2,        4,       1, '-12340.0123', '-1.234001e04'],
            [2,        4,       2, '-12340.0123', '-1.234001x10^4'],
            [2,        4,       3, '-12340.0123', '-1.234001x10<sup>4</sup>'],
            [2,        4,       4, '-12340.0123', '-1.234001·10^4'],
            [2,        4,       5, '-12340.0123', '-1.234001·10<sup>4</sup>'],
        ]
        s = self.service
        s.setLowerDetectionLimit('-99999') # We want to test results below 0 too
        prevm = []
        an = None
        bs = self.portal.bika_setup
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
                prevm = m
            an.setResult(m[3])

            self.assertEqual(an.getResult(), m[3])
            self.assertEqual(an.Schema().getField('Result').get(an), m[3])
            fr = an.getFormattedResult(sciformat=m[2])
            # print '%s   %s   %s   %s  =>  \'%s\' ?= \'%s\'' % (m[0],m[1],m[2],m[3],m[4],fr)
            self.assertEqual(fr, m[4])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDecimalSciNotation))
    return suite
