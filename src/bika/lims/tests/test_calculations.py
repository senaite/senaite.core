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
from bika.lims.workflow import doActionFor
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, setRoles

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


class TestCalculations(DataTestCase):

    def setUp(self):
        super(TestCalculations, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ['Member', 'LabManager'])
        login(self.portal, TEST_USER_NAME)

        # Calculation: Total Hardness
        # Initial formula: [Ca] + [Mg]
        calcs = self.portal.bika_setup.bika_calculations
        self.calculation = [calcs[k] for k in calcs
                            if calcs[k].title == 'Total Hardness'][0]

        # Service with calculation: Tot. Hardness (THCaCO3)
        servs = self.portal.bika_setup.bika_analysisservices
        self.calcservice = [servs[k] for k in servs
                            if servs[k].title == 'Tot. Hardness (THCaCO3)'][0]
        self.assertEqual(self.calcservice.getCalculation(), self.calculation)
        self.calcservice.setUseDefaultCalculation(False)

        # Analysis Services: Ca and Mg
        self.services = [servs[k] for k in servs
                         if servs[k].getKeyword() in ('Ca', 'Mg')]

        # Allow Manual DLs
        for s in self.services:
            s.setLowerDetectionLimit('10')
            s.setUpperDetectionLimit('20')
            s.setDetectionLimitSelector(True)
            s.setAllowManualDetectionLimit(True)

        # Formulas to test
        # Ca and Mg detection Limits: LDL: 10, UDL: 20
        self.formulas = [

            {'formula' : '[Ca]+[Mg]',
             'analyses': {'Ca':'10', 'Mg': '15'},
             'interims': {},
             'exresult': '25'
            },

            {'formula' : '[Ca]+[Mg]',
             'analyses': {'Ca':'-20', 'Mg': '5'},
             'interims': {},
             'exresult': '-15'
            },

            {'formula' : '[Ca]+[Mg]+[IN1]',
             'analyses': {'Ca': '10', 'Mg': '15'},
             'interims': {'IN1':'2'},
             'exresult': '27'
            },

            {'formula' : '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '5', 'Mg': '1'},
             'interims': {'IN1':'5'},
             'exresult': '15'
            },

            {'formula' : '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '10', 'Mg': '1'},
             'interims': {'IN1':'5'},
             'exresult': '16'
            },

            {'formula' : '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '10', 'Mg': '2'},
             'interims': {'IN1':'5'},
             'exresult': '17'
            },

            {'formula' : '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '15', 'Mg': '2'},
             'interims': {'IN1':'5'},
             'exresult': '22'
            },

            {'formula' : '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '15', 'Mg': '3'},
             'interims': {'IN1':'5'},
             'exresult': '23'
            },

            {'formula' : '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '20', 'Mg': '3'},
             'interims': {'IN1':'5'},
             'exresult': '28'
            },

            {'formula' : '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '20', 'Mg': '3'},
             'interims': {'IN1':'10'},
             'exresult': '33'
            },

            {'formula' : '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '30', 'Mg': '3'},
             'interims': {'IN1':'10'},
             'exresult': '50'
            },

            {'formula' : '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '>30', 'Mg': '5'},
             'interims': {'IN1':'10'},
             'exresult': '60'
            },

            {'formula' : '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '<5', 'Mg': '5'},
             'interims': {'IN1':'10'},
             'exresult': '10'
            },
        ]
        # New formulas for precision testing
        self.formulas_precision = [
            {'formula' : '[Ca]/[Mg]',
             'analyses': {'Ca':'10', 'Mg': '15'},
             'interims': {},
             'test_fixed_precision': [
                {'fixed_precision': 5,
                 'expected_result': '0.66667',
                },
                {'fixed_precision': 2,
                 'expected_result': '0.67'
                },
                {'fixed_precision': 1,
                 'expected_result': '0.7'
                },
                {'fixed_precision': 0,
                 'expected_result': '1'
                },
                {'fixed_precision': -1,
                 'expected_result': '1'
                },
                {'fixed_precision': -5,
                 'expected_result': '1'
                },
            ],
            'test_uncertainties_precision':[
                    {'uncertainties': [
                        {'intercept_min': 0, 'intercept_max': 10, 'errorvalue': 0.056},
                        ],
                    'expected_result': '0.67'
                    },
                    {'uncertainties': [
                        {'intercept_min': 0.002, 'intercept_max': 20, 'errorvalue': 0.1}
                        ],
                    'expected_result': '0.7'
                    },
                ],
            },
            {'formula' : '[Ca]/[Mg]*[IN1]',
             'analyses': {'Ca':'100', 'Mg': '20'},
             'interims': {'IN1':'0.12'},
             'test_fixed_precision': [
                {'fixed_precision': 5,
                 'expected_result': '0.60000',
                },
                {'fixed_precision': 2,
                 'expected_result': '0.60'
                },
                {'fixed_precision': 1,
                 'expected_result': '0.6'
                },
                {'fixed_precision': 0,
                 'expected_result': '1'
                },
                {'fixed_precision': -1,
                 'expected_result': '1'
                },
                {'fixed_precision': -5,
                 'expected_result': '1'
                },
            ],
            'test_uncertainties_precision':[
                    {'uncertainties': [
                        {'intercept_min': 0, 'intercept_max': 10, 'errorvalue': 0.1},
                        {'intercept_min': 11, 'intercept_max': 20, 'errorvalue': 0.056}
                        ],
                    'expected_result': '0.6'
                    },
                    {'uncertainties': [
                        {'intercept_min': 0.1, 'intercept_max': 0.6, 'errorvalue': 0.1},
                        {'intercept_min': 0.66, 'intercept_max': 20, 'errorvalue': 0.056}
                        ],
                    'expected_result': '0.6',
                     },
                ],
            },
            {'formula' : '[Ca]/[Mg]',
             'analyses': {'Ca':'10', 'Mg': 1},
             'interims': {},
             'test_fixed_precision': [
                {'fixed_precision': 5,
                 'expected_result': '10.00000',
                },
                {'fixed_precision': 2,
                 'expected_result': '10.00'
                },
                {'fixed_precision': 1,
                 'expected_result': '10.0'
                },
                {'fixed_precision': 0,
                 'expected_result': '10'
                },
                {'fixed_precision': -1,
                 'expected_result': '10'
                },
                {'fixed_precision': -5,
                 'expected_result': '10'
                },
            ],
            'test_uncertainties_precision':[
                    {'uncertainties': [
                        {'intercept_min': 0, 'intercept_max': 10, 'errorvalue': 0.1},
                        {'intercept_min': 11, 'intercept_max': 20, 'errorvalue': 0.056}
                        ],
                    'expected_result': '10.0'
                    },
                ],
            },
            {'formula' : '[Ca]/[Mg]',
             'analyses': {'Ca':'1', 'Mg': '20'},
             'interims': {},
             'test_fixed_precision': [
                {'fixed_precision': 5,
                 'expected_result': '0.05000',
                },
                {'fixed_precision': 2,
                 'expected_result': '0.05'
                },
                {'fixed_precision': 1,
                 'expected_result': '0.1'
                },
                {'fixed_precision': 0,
                 'expected_result': '0'
                },
                {'fixed_precision': -1,
                 'expected_result': '0'
                },
                {'fixed_precision': -5,
                 'expected_result': '0'
                },
            ],
            'test_uncertainties_precision':[
                    {'uncertainties': [
                        {'intercept_min': 0, 'intercept_max': 0.01, 'errorvalue': 0.01},
                        {'intercept_min': 11, 'intercept_max': 20, 'errorvalue': 0.056}
                        ],
                    'expected_result': '0.05'
                    },
                ],
            },
            {'formula': '([Ca]/[Mg])+0.000001',
             'analyses': {'Ca': '1', 'Mg': '20'},
             'interims': {},
             'test_fixed_precision': [
                 {'fixed_precision': 6,
                  'expected_result': '0.050001',
                  },
             ],
             'test_uncertainties_precision': [
                 {'uncertainties': [
                     {'intercept_min': 0, 'intercept_max': 0.09,
                      'errorvalue': 0},
                 ],
                     'expected_result': '0.050001'
                 },
             ],
             },

        ]

    def tearDown(self):
        # Service with calculation: Tot. Harndess (THCaCO3)
        self.calculation.setFormula('[Ca] + [Mg]')
        self.calcservice.setUseDefaultCalculation(True)

        # Allow Manual DLs
        for s in self.services:
            s.setLowerDetectionLimit('0')
            s.setUpperDetectionLimit('10000')
            s.setAllowManualDetectionLimit(False)

        super(TestCalculations, self).tearDown()

    def test_analysis_method_calculation(self):
        # Input results
        # Client:       Happy Hills
        # SampleType:   Apple Pulp
        # Contact:      Rita Mohale
        # Analyses:     [Calcium, Mg, Total Hardness]
        from bika.lims.utils.analysisrequest import create_analysisrequest
        for f in self.formulas:
            # Set custom calculation
            self.calculation.setFormula(f['formula'])
            self.assertEqual(self.calculation.getFormula(), f['formula'])
            interims = []
            for k,v in f['interims'].items():
                interims.append({'keyword': k, 'title': k, 'value': v,
                                 'hidden': False, 'type': 'int',
                                 'unit': ''})
            self.calculation.setInterimFields(interims)
            self.assertEqual(self.calculation.getInterimFields(), interims)

            # Create the AR
            client = self.portal.clients['client-1']
            sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
            values = {'Client': client.UID(),
                      'Contact': client.getContacts()[0].UID(),
                      'SamplingDate': '2015-01-01',
                      'SampleType': sampletype.UID()}
            request = {}
            services = [s.UID() for s in self.services] + [self.calcservice.UID()]
            ar = create_analysisrequest(client, request, values, services)
            doActionFor(ar, 'receive')
            # Set results and interims
            calcanalysis = None
            for an in ar.getAnalyses():
                an = an.getObject()
                key = an.getKeyword()
                if key in f['analyses']:
                    an.setResult(f['analyses'][key])
                    if an.isLowerDetectionLimit() \
                        or an.isUpperDetectionLimit():
                        operator = an.getDetectionLimitOperand()
                        strres = f['analyses'][key].replace(operator, '')
                        self.assertEqual(an.getResult(), float(strres))
                    else:
                        self.assertEqual(an.getResult(), f['analyses'][key])
                elif key == self.calcservice.getKeyword():
                    calcanalysis = an

                # Set interims
                interims = an.getInterimFields()
                intermap = []
                for i in interims:
                    if i['keyword'] in f['interims']:
                        ival = float(f['interims'][i['keyword']])
                        intermap.append({'keyword': i['keyword'],
                                        'value': ival,
                                        'title': i['title'],
                                        'hidden': i['hidden'],
                                        'type': i['type'],
                                        'unit': i['unit']})
                    else:
                        intermap.append(i)
                an.setInterimFields(intermap)
                self.assertEqual(an.getInterimFields(), intermap)

            # Let's go.. calculate and check result
            success = calcanalysis.calculateResult(True, True)
            self.assertTrue(success, True)
            self.assertNotEqual(calcanalysis.getResult(), '',
                'getResult returns an empty string')
            self.assertEqual(float(calcanalysis.getResult()), float(f['exresult']))

    def test_calculation_fixed_precision(self):
        # Input results
        # Client:       Happy Hills
        # SampleType:   Apple Pulp
        # Contact:      Rita Mohale
        # Analyses:     [Calcium, Mg, Total Hardness]
        from bika.lims.utils.analysisrequest import create_analysisrequest
        for f in self.formulas_precision:
            self.calculation.setFormula(f['formula'])
            self.assertEqual(self.calculation.getFormula(), f['formula'])
            interims = []
            for k,v in f['interims'].items():
                interims.append({'keyword': k, 'title':k, 'value': v,
                                 'hidden': False, 'type': 'int',
                                 'unit': ''});
            self.calculation.setInterimFields(interims)
            self.assertEqual(self.calculation.getInterimFields(), interims)

            for case in f['test_fixed_precision']:
                # Define precision
                services_obj = [s for s in self.services] + [self.calcservice]
                for service in services_obj:
                    service.setPrecision(case['fixed_precision'])
                # Create the AR
                client = self.portal.clients['client-1']
                sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
                values = {'Client': client.UID(),
                          'Contact': client.getContacts()[0].UID(),
                          'SamplingDate': '2015-01-01',
                          'SampleType': sampletype.UID()}
                request = {}
                services = [s.UID() for s in self.services] + [self.calcservice.UID()]
                ar = create_analysisrequest(client, request, values, services)
                doActionFor(ar, 'receive')

                # Set results and interims
                calcanalysis = None
                for an in ar.getAnalyses():
                    an = an.getObject()
                    key = an.getKeyword()
                    if key in f['analyses']:
                        an.setResult(f['analyses'][key])
                        if an.isLowerDetectionLimit() \
                            or an.isUpperDetectionLimit():
                            operator = an.getDetectionLimitOperand()
                            strres = f['analyses'][key].replace(operator, '')
                            self.assertEqual(an.getResult(), str(float(strres)))
                        else:
                            # The analysis' results have to be always strings
                            self.assertEqual(an.getResult(), str(f['analyses'][key]))
                    elif key == self.calcservice.getKeyword():
                        calcanalysis = an

                    # Set interims
                    interims = an.getInterimFields()
                    intermap = []
                    for i in interims:
                        if i['keyword'] in f['interims']:
                            ival = float(f['interims'][i['keyword']])
                            intermap.append({'keyword': i['keyword'],
                                             'value': ival,
                                             'title': i['title'],
                                             'hidden': i['hidden'],
                                             'type': i['type'],
                                             'unit': i['unit']})
                        else:
                            intermap.append(i)
                    an.setInterimFields(intermap)
                    self.assertEqual(an.getInterimFields(), intermap)

                # Let's go.. calculate and check result
                calcanalysis.calculateResult(True, True)
                self.assertEqual(calcanalysis.getFormattedResult(), case['expected_result'])

    def test_calculation_uncertainties_precision(self):
        # Input results
        # Client:       Happy Hills
        # SampleType:   Apple Pulp
        # Contact:      Rita Mohale
        # Analyses:     [Calcium, Mg, Total Hardness]
        from bika.lims.utils.analysisrequest import create_analysisrequest
        for f in self.formulas_precision:
            self.calculation.setFormula(f['formula'])
            self.assertEqual(self.calculation.getFormula(), f['formula'])
            interims = []
            for k, v in f['interims'].items():
                interims.append({'keyword': k, 'title': k, 'value': v,
                                 'hidden': False, 'type': 'int',
                                 'unit': ''})
            self.calculation.setInterimFields(interims)
            self.assertEqual(self.calculation.getInterimFields(), interims)

            for case in f['test_uncertainties_precision']:
                # Define precision
                services_obj = [s for s in self.services] + [self.calcservice]

                for service in services_obj:
                    service.setPrecisionFromUncertainty(True)
                    service.setUncertainties(case['uncertainties'])
                # Create the AR
                client = self.portal.clients['client-1']
                sampletype = self.portal.bika_setup.bika_sampletypes['sampletype-1']
                values = {'Client': client.UID(),
                          'Contact': client.getContacts()[0].UID(),
                          'SamplingDate': '2015-01-01',
                          'SampleType': sampletype.UID()}
                request = {}
                services = [s.UID() for s in self.services] + [self.calcservice.UID()]
                ar = create_analysisrequest(client, request, values, services)
                doActionFor(ar, 'receive')

                # Set results and interims
                calcanalysis = None
                for an in ar.getAnalyses():
                    an = an.getObject()
                    key = an.getKeyword()
                    if key in f['analyses']:
                        an.setResult(f['analyses'][key])
                        if an.isLowerDetectionLimit() \
                            or an.isUpperDetectionLimit():
                            operator = an.getDetectionLimitOperand()
                            strres = f['analyses'][key].replace(operator, '')
                            self.assertEqual(an.getResult(), str(float(strres)))
                        else:
                            # The analysis' results have to be always strings
                            self.assertEqual(an.getResult(), str(f['analyses'][key]))
                    elif key == self.calcservice.getKeyword():
                        calcanalysis = an

                    # Set interims
                    interims = an.getInterimFields()
                    intermap = []
                    for i in interims:
                        if i['keyword'] in f['interims']:
                            ival = float(f['interims'][i['keyword']])
                            intermap.append({'keyword': i['keyword'],
                                             'value': ival,
                                             'title': i['title'],
                                             'hidden': i['hidden'],
                                             'type': i['type'],
                                             'unit': i['unit']})
                        else:
                            intermap.append(i)
                    an.setInterimFields(intermap)
                    self.assertEqual(an.getInterimFields(), intermap)

                # Let's go.. calculate and check result
                success = calcanalysis.calculateResult(True, True)
                self.assertTrue(success, True)
                self.assertEqual(
                    calcanalysis.getFormattedResult(),
                    case['expected_result'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCalculations))
    return suite
