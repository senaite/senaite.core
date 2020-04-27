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


class TestLimitDetections(DataTestCase):

    def setUp(self):
        super(TestLimitDetections, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ['Member', 'LabManager'])
        login(self.portal, TEST_USER_NAME)
        servs = self.portal.bika_setup.bika_analysisservices
        # analysis-service-3: Calcium (Ca)
        # analysis-service-6: Cooper (Cu)
        # analysis-service-7: Iron (Fe)
        self.services = [servs['analysisservice-3'],
                         servs['analysisservice-6'],
                         servs['analysisservice-7']]
        self.lds = [{'min': '0',  'max': '1000', 'manual': False},
                    {'min': '10', 'max': '20',   'manual': True},
                    {'min': '0',  'max': '20',   'manual': True}]
        idx = 0
        for s in self.services:
            s.setDetectionLimitSelector(self.lds[idx]['manual'])
            s.setAllowManualDetectionLimit(self.lds[idx]['manual'])
            s.setLowerDetectionLimit(self.lds[idx]['min'])
            s.setUpperDetectionLimit(self.lds[idx]['max'])
            idx += 1

    def tearDown(self):
        for s in self.services:
            s.setDetectionLimitSelector(False)
            s.setAllowManualDetectionLimit(False)
            s.setLowerDetectionLimit(str(0))
            s.setUpperDetectionLimit(str(1000))
        super(TestLimitDetections, self).tearDown()

    def test_ar_manage_results_detectionlimit_selector_manual(self):
        cases = [

            # ROUND 1 ---------------------
            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : False,
             'manual'            : False,
             'input'             : '5',
             'expresult'         : 5.0,
             'expformattedresult': '< 10',
             'isbelowldl'        : True,
             'isaboveudl'        : False,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : False,
             'manual'            : False,
             'input'             : '15',
             'expresult'         : 15.0,
             'expformattedresult': '15.00',
             'isbelowldl'        : False,
             'isaboveudl'        : False,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : False,
             'manual'            : False,
             'input'             : '25',
             'expresult'         : 25.0,
             'expformattedresult': '> 20',
             'isbelowldl'        : False,
             'isaboveudl'        : True,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : False,
             'manual'            : False,
             'input'             : '<5',
             'expresult'         : 5.0, # '<' assignment not allowed
             'expformattedresult': '< 10',
             'isbelowldl'        : True,
             'isaboveudl'        : False,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : False,
             'manual'            : False,
             'input'             : '<15',
             'expresult'         : 15.0, # '<' assignment not allowed
             'expformattedresult': '15.00',
             'isbelowldl'        : False,
             'isaboveudl'        : False,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : False,
             'manual'            : False,
             'input'             : '>15',
             'expresult'         : 15.0, # '>' assignment not allowed
             'expformattedresult': '15.00',
             'isbelowldl'        : False,
             'isaboveudl'        : False,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : False,
             'manual'            : False,
             'input'             : '25',
             'expresult'         : 25.0, # '>' assignment not allowed
             'expformattedresult': '> 20',
             'isbelowldl'        : False,
             'isaboveudl'        : True,
             'isldl'             : False,
             'isudl'             : False},

            # ROUND 2 ---------------------
            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : False,
             'input'             : '5',
             'expresult'         : 5.0,
             'expformattedresult': '< 10',
             'isbelowldl'        : True,
             'isaboveudl'        : False,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : False,
             'input'             : '15',
             'expresult'         : 15.0,
             'expformattedresult': '15.00',
             'isbelowldl'        : False,
             'isaboveudl'        : False,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : False,
             'input'             : '25',
             'expresult'         : 25.0,
             'expformattedresult': '> 20',
             'isbelowldl'        : False,
             'isaboveudl'        : True,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : False,
             'input'             : '<5',
             'expresult'         : 10.0, # '<' assignment allowed, but not custom
             'expformattedresult': '< 10',
             'isbelowldl'        : True,
             'isaboveudl'        : False,
             'isldl'             : True,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : False,
             'input'             : '<15',
             'expresult'         : 10.0, # '<' assignment allowed, but not custom
             'expformattedresult': '< 10',
             'isbelowldl'        : True,
             'isaboveudl'        : False,
             'isldl'             : True,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : False,
             'input'             : '>15',
             'expresult'         : 20.0, # '>' assignment allowed, but not custom
             'expformattedresult': '> 20',
             'isbelowldl'        : False,
             'isaboveudl'        : True,
             'isldl'             : False,
             'isudl'             : True},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : False,
             'input'             : '>25',
             'expresult'         : 20.0, # '>' assignment allowed, but not custom
             'expformattedresult': '> 20',
             'isbelowldl'        : False,
             'isaboveudl'        : True,
             'isldl'             : False,
             'isudl'             : True},

            # ROUND 3 ---------------------
            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : True,
             'input'             : '5',
             'expresult'         : 5.0,
             'expformattedresult': '< 10',
             'isbelowldl'        : True,
             'isaboveudl'        : False,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : True,
             'input'             : '15',
             'expresult'         : 15.0,
             'expformattedresult': '15.00',
             'isbelowldl'        : False,
             'isaboveudl'        : False,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : True,
             'input'             : '25',
             'expresult'         : 25.0,
             'expformattedresult': '> 20',
             'isbelowldl'        : False,
             'isaboveudl'        : True,
             'isldl'             : False,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : True,
             'input'             : '<5',
             'expresult'         : 5.0, # '<' assignment allowed
             'expformattedresult': '< 5',
             'isbelowldl'        : True,
             'isaboveudl'        : False,
             'isldl'             : True,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : True,
             'input'             : '<15',
             'expresult'         : 15.0, # '<' assignment allowed
             'expformattedresult': '< 15',
             'isbelowldl'        : True,
             'isaboveudl'        : False,
             'isldl'             : True,
             'isudl'             : False},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : True,
             'input'             : '>15',
             'expresult'         : 15.0, # '>' assignment allowed
             'expformattedresult': '> 15',
             'isbelowldl'        : False,
             'isaboveudl'        : True,
             'isldl'             : False,
             'isudl'             : True},

            {'min'               : '10',
             'max'               : '20',
             'displaydl'         : True,
             'manual'            : True,
             'input'             : '>25',
             'expresult'         : 25.0, # '>' assignment allowed
             'expformattedresult': '> 25',
             'isbelowldl'        : False,
             'isaboveudl'        : True,
             'isldl'             : False,
             'isudl'             : True},
        ]

        for num, case in enumerate(cases):
            s = self.services[0]
            s.setDetectionLimitSelector(case['displaydl'])
            s.setAllowManualDetectionLimit(case['manual'])
            s.setLowerDetectionLimit(case['min'])
            s.setUpperDetectionLimit(case['max'])

            # Input results
            # Client:       Happy Hills
            # SampleType:   Apple Pulp
            # Contact:      Rita Mohale
            # Analyses:     [Calcium, Copper]
            client = self.portal.clients['client-1']
            sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
            values = {'Client': client.UID(),
                      'Contact': client.getContacts()[0].UID(),
                      'SamplingDate': '2015-01-01',
                      'SampleType': sampletype.UID()}
            request = {}
            ar = create_analysisrequest(client, request, values, [s.UID()])
            wf = getToolByName(ar, 'portal_workflow')
            wf.doActionFor(ar, 'receive')

            an = ar.getAnalyses()[0].getObject()
            an.setResult(case['input'])
            self.assertEqual(an.isBelowLowerDetectionLimit(), case['isbelowldl'], case)
            self.assertEqual(an.isAboveUpperDetectionLimit(), case['isaboveudl'], case)
            self.assertEqual(an.isLowerDetectionLimit(), case['isldl'], case)
            self.assertEqual(an.isUpperDetectionLimit(), case['isudl'], case)
            self.assertEqual(float(an.getResult()), case['expresult'], case)
            self.assertEqual(an.getFormattedResult(html=False), case['expformattedresult'], case)
            expres = case['expformattedresult']
            expres = expres.replace('< ', '&lt; ') if an.isBelowLowerDetectionLimit() else expres
            expres = expres.replace('> ', '&gt; ') if an.isAboveUpperDetectionLimit() else expres
            self.assertEqual(an.getFormattedResult(html=True), expres, case)
            self.assertEqual(an.getFormattedResult(), expres, case)

    def test_ar_manageresults_limitdetections(self):
        # Input results
        # Client:       Happy Hills
        # SampleType:   Apple Pulp
        # Contact:      Rita Mohale
        # Analyses:     [Calcium, Copper]
        client = self.portal.clients['client-1']
        sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
        values = {'Client': client.UID(),
                  'Contact': client.getContacts()[0].UID(),
                  'SamplingDate': '2015-01-01',
                  'SampleType': sampletype.UID()}
        request = {}
        services = [s.UID() for s in self.services]
        ar = create_analysisrequest(client, request, values, services)

        # Basic detection limits
        asidxs = {'Ca': 0, # analysisservice-3
                  'Cu': 1, # analysisservice-6
                  'Fe': 2} # analysisservice-7
        ans = ar.getAnalyses()
        # Sort them by getKeyword, so we get them in the same order as the ASs
        ans = sorted(ans, key=lambda x: x.getKeyword)
        for a in ans:
            an = a.getObject()
            idx = asidxs[an.id]
            self.assertEqual(an.getLowerDetectionLimit(), float(self.lds[idx]['min']))
            self.assertEqual(an.getUpperDetectionLimit(), float(self.lds[idx]['max']))
            self.assertEqual(an.getAllowManualDetectionLimit(), self.lds[idx]['manual'])

            # Empty result
            self.assertFalse(an.getDetectionLimitOperand())
            self.assertFalse(an.isBelowLowerDetectionLimit())
            self.assertFalse(an.isAboveUpperDetectionLimit())

            # Set a result
            an.setResult('15')
            self.assertEqual(float(an.getResult()), 15)
            self.assertFalse(an.isBelowLowerDetectionLimit())
            self.assertFalse(an.isAboveUpperDetectionLimit())
            self.assertFalse(an.getDetectionLimitOperand())
            self.assertEqual(an.getFormattedResult(), '15.00')
            self.assertEqual(an.getFormattedResult(html=True), '15.00')
            self.assertEqual(an.getFormattedResult(html=False), '15.00')
            an.setResult('-1')
            self.assertEqual(float(an.getResult()), -1)
            self.assertTrue(an.isBelowLowerDetectionLimit())
            self.assertFalse(an.isAboveUpperDetectionLimit())
            self.assertFalse(an.getDetectionLimitOperand())
            self.assertEqual(an.getFormattedResult(html=False), '< %s' % (self.lds[idx]['min']))
            self.assertEqual(an.getFormattedResult(html=True), '&lt; %s' % (self.lds[idx]['min']))
            self.assertEqual(an.getFormattedResult(), '&lt; %s' % (self.lds[idx]['min']))
            an.setResult('2000')
            self.assertEqual(float(an.getResult()), 2000)
            self.assertFalse(an.isBelowLowerDetectionLimit())
            self.assertTrue(an.isAboveUpperDetectionLimit())
            self.assertFalse(an.getDetectionLimitOperand())
            self.assertEqual(an.getFormattedResult(html=False), '> %s' % (self.lds[idx]['max']))
            self.assertEqual(an.getFormattedResult(html=True), '&gt; %s' % (self.lds[idx]['max']))
            self.assertEqual(an.getFormattedResult(), '&gt; %s' % (self.lds[idx]['max']))

            # Set a DL result
            an.setResult('<15')
            self.assertEqual(float(an.getResult()), 15)
            if self.lds[idx]['manual']:
                self.assertTrue(an.isBelowLowerDetectionLimit())
                self.assertFalse(an.isAboveUpperDetectionLimit())
                self.assertEqual(an.getDetectionLimitOperand(), '<')
                self.assertEqual(an.getFormattedResult(html=False), '< 15')
                self.assertEqual(an.getFormattedResult(html=True), '&lt; 15')
                self.assertEqual(an.getFormattedResult(), '&lt; 15')
            else:
                self.assertFalse(an.isBelowLowerDetectionLimit())
                self.assertFalse(an.isAboveUpperDetectionLimit())
                self.assertFalse(an.getDetectionLimitOperand())
                self.assertEqual(an.getFormattedResult(html=False), '15.00')
                self.assertEqual(an.getFormattedResult(html=True), '15.00')
                self.assertEqual(an.getFormattedResult(), '15.00')

            an.setResult('>15')
            self.assertEqual(float(an.getResult()), 15)
            if self.lds[idx]['manual']:
                self.assertFalse(an.isBelowLowerDetectionLimit())
                self.assertTrue(an.isAboveUpperDetectionLimit())
                self.assertEqual(an.getDetectionLimitOperand(), '>')
                self.assertEqual(an.getFormattedResult(html=False), '> 15')
                self.assertEqual(an.getFormattedResult(html=True), '&gt; 15')
                self.assertEqual(an.getFormattedResult(), '&gt; 15')
            else:
                self.assertFalse(an.isBelowLowerDetectionLimit())
                self.assertFalse(an.isAboveUpperDetectionLimit())
                self.assertFalse(an.getDetectionLimitOperand())
                self.assertEqual(an.getFormattedResult(html=False), '15.00')
                self.assertEqual(an.getFormattedResult(html=True), '15.00')
                self.assertEqual(an.getFormattedResult(), '15.00')

            # Set a DL result explicitely
            an.setDetectionLimitOperand('<')
            an.setResult('15')
            self.assertEqual(float(an.getResult()), 15)
            if self.lds[idx]['manual']:
                self.assertTrue(an.isBelowLowerDetectionLimit())
                self.assertFalse(an.isAboveUpperDetectionLimit())
                self.assertEqual(an.getDetectionLimitOperand(), '<')
                self.assertEqual(an.getFormattedResult(html=False), '< 15')
                self.assertEqual(an.getFormattedResult(html=True), '&lt; 15')
                self.assertEqual(an.getFormattedResult(), '&lt; 15')
            else:
                self.assertFalse(an.isBelowLowerDetectionLimit())
                self.assertFalse(an.isAboveUpperDetectionLimit())
                self.assertFalse(an.getDetectionLimitOperand())
                self.assertEqual(an.getFormattedResult(html=False), '15.00')
                self.assertEqual(an.getFormattedResult(html=True), '15.00')
                self.assertEqual(an.getFormattedResult(), '15.00')

            an.setDetectionLimitOperand('>')
            an.setResult('15')
            self.assertEqual(float(an.getResult()), 15)
            if self.lds[idx]['manual']:
                self.assertFalse(an.isBelowLowerDetectionLimit())
                self.assertTrue(an.isAboveUpperDetectionLimit())
                self.assertEqual(an.getDetectionLimitOperand(), '>')
                self.assertEqual(an.getFormattedResult(html=False), '> 15')
                self.assertEqual(an.getFormattedResult(html=True), '&gt; 15')
                self.assertEqual(an.getFormattedResult(), '&gt; 15')
            else:
                self.assertFalse(an.isBelowLowerDetectionLimit())
                self.assertFalse(an.isAboveUpperDetectionLimit())
                self.assertFalse(an.getDetectionLimitOperand())
                self.assertEqual(an.getFormattedResult(html=False), '15.00')
                self.assertEqual(an.getFormattedResult(html=True), '15.00')
                self.assertEqual(an.getFormattedResult(), '15.00')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLimitDetections))
    return suite
