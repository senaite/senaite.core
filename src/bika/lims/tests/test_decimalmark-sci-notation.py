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


class TestDecimalMarkWithSciNotation(DataTestCase):

    def setUp(self):
        super(TestDecimalMarkWithSciNotation, self).setUp()
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
        self.orig_dm = self.portal.bika_setup.getResultsDecimalMark()

    def tearDown(self):
        self.portal.bika_setup.setExponentialFormatThreshold(self.orig_bs_expf)
        self.portal.bika_setup.setScientificNotationResults(self.orig_bs_scin)
        self.service.setPrecision(self.orig_as_prec)
        self.service.setExponentialFormatPrecision(self.orig_as_expf)
        self.service.setLowerDetectionLimit(self.orig_as_ldl)
        self.portal.bika_setup.setResultsDecimalMark(self.orig_dm)
        super(TestDecimalMarkWithSciNotation, self).tearDown()

    def test_DecimalMarkWithSciNotation(self):
        # Notations
        # '1' => aE+b / aE-b
        # '2' => ax10^b / ax10^-b
        # '3' => ax10^b / ax10^-b (with superscript)
        # '4' => a·10^b / a·10^-b
        # '5' => a·10^b / a·10^-b (with superscript)
        matrix = [
            # as_prec  as_exp  not  decimalmark result    formatted result
            # -------  ------  ---  ----------- --------  --------------------
            [0,        0,      1, '0',            '0'],
            [0,        0,      2, '0',            '0'],
            [0,        0,      3, '0',            '0'],
            [0,        0,      4, '0',            '0'],
            [0,        0,      5, '0',            '0'],
            [2,        5,      1, '0.01',         '0,01'],
            [2,        5,      2, '0.01',         '0,01'],
            [2,        5,      3, '0.01',         '0,01'],
            [2,        5,      4, '0.01',         '0,01'],
            [2,        5,      5, '0.01',         '0,01'],
            [2,        1,      1, '0.123',        '1,2e-01'],
            [2,        1,      2, '0.123',        '1,2x10^-1'],
            [2,        1,      3, '0.123',        '1,2x10<sup>-1</sup>'],
            [2,        1,      4, '0.123',        '1,2·10^-1'],
            [2,        1,      5, '0.123',        '1,2·10<sup>-1</sup>'],
            [2,        1,      1, '1.234',        '1,23'],
            [2,        1,      2, '1.234',        '1,23'],
            [2,        1,      3, '1.234',        '1,23'],
            [2,        1,      4, '1.234',        '1,23'],
            [2,        1,      5, '1.234',        '1,23'],
            [2,        1,      1, '12.345',       '1,235e01'],
            [2,        1,      2, '12.345',       '1,235x10^1'],
            [2,        1,      3, '12.345',       '1,235x10<sup>1</sup>'],
            [2,        1,      4, '12.345',       '1,235·10^1'],
            [2,        1,      5, '12.345',       '1,235·10<sup>1</sup>'],
            [4,        3,      1, '-123.45678',    '-123,4568'],
            [4,        3,      2, '-123.45678',    '-123,4568'],
            [4,        3,      3, '-123.45678',    '-123,4568'],
            [4,        3,      4, '-123.45678',    '-123,4568'],
            [4,        3,      5, '-123.45678',    '-123,4568'],
            [4,        3,      1, '-1234.5678',    '-1,2345678e03'],
            [4,        3,      2, '-1234.5678',    '-1,2345678x10^3'],
            [4,        3,      3, '-1234.5678',    '-1,2345678x10<sup>3</sup>'],
            [4,        3,      4, '-1234.5678',    '-1,2345678·10^3'],
            [4,        3,      5, '-1234.5678',    '-1,2345678·10<sup>3</sup>'],
        ]
        s = self.service
        s.setLowerDetectionLimit('-99999') # We want to test results below 0 too
        prevm = []
        an = None
        bs = self.portal.bika_setup
        bs.setResultsDecimalMark(',')
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
            fr = an.getFormattedResult(sciformat=m[2],decimalmark=bs.getResultsDecimalMark())
            # print '%s   %s   %s   %s  =>  \'%s\' ?= \'%s\'' % (m[0],m[1],m[2],m[3],m[4],fr)
            self.assertEqual(fr, m[4])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDecimalMarkWithSciNotation))
    return suite
