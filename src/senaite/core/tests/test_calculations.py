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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import unittest2 as unittest
from bika.lims.workflow import doActionFor
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from senaite.core.browser.form.adapters.calculation import EditForm
from senaite.core.browser.form.adapters.calculation import FIELD_FORMULA
from senaite.core.browser.form.adapters.calculation import FIELD_TEST_KEYWORD
from senaite.core.browser.form.adapters.calculation import FIELD_TEST_RESULT
from senaite.core.browser.form.adapters.calculation import FIELD_TEST_VALUE
from senaite.core.content.calculation import Calculation
from senaite.core.content.calculation import ICalculationSchema
from senaite.core.content.calculation import calculate_formula
from senaite.core.tests.base import DataTestCase
from zope.lifecycleevent import modified


class TestCalculations(DataTestCase):

    def setUp(self):
        super(TestCalculations, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ['Member', 'LabManager'])
        login(self.portal, TEST_USER_NAME)

        # Calculation: Total Hardness
        # Initial formula: [Ca] + [Mg]
        calcs = self.portal.setup.calculations
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
            {
                'formula': '[Ca]+[Mg]',
                'analyses': {'Ca': '10', 'Mg': '15'},
                'interims': {},
                'exresult': '25.0'
            },

            {
                'formula': '[Ca]+[Mg]',
                'analyses': {'Ca': '-20', 'Mg': '5'},
                'interims': {},
                'exresult': '-15.0'
            },

            {'formula': '[Ca]+[Mg]+[IN1]',
             'analyses': {'Ca': '10', 'Mg': '15'},
             'interims': {'IN1': '2'},
             'exresult': '27.0'
             },

            {'formula': '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '5', 'Mg': '1'},
             'interims': {'IN1': '5'},
             'exresult': '15.0'
             },

            {'formula': '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '10', 'Mg': '1'},
             'interims': {'IN1': '5'},
             'exresult': '16.0'
             },

            {'formula': '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '10', 'Mg': '2'},
             'interims': {'IN1': '5'},
             'exresult': '17.0'
             },

            {'formula': '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '15', 'Mg': '2'},
             'interims': {'IN1': '5'},
             'exresult': '22.0'
             },

            {'formula': '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '15', 'Mg': '3'},
             'interims': {'IN1': '5'},
             'exresult': '23.0'
             },

            {'formula': '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '20', 'Mg': '3'},
             'interims': {'IN1': '5'},
             'exresult': '28.0'
             },

            {'formula': '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '20', 'Mg': '3'},
             'interims': {'IN1': '10'},
             'exresult': '33.0'
             },

            {'formula': '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '30', 'Mg': '3'},
             'interims': {'IN1': '10'},
             'exresult': '50.0'
             },

            {'formula': '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '>30', 'Mg': '5'},
             'interims': {'IN1': '10'},
             'exresult': '60.0'
             },

            {'formula': '([Ca]+[Ca.LDL]) if [Ca.BELOWLDL] else (([Ca.UDL] + [Ca]) if [Ca.ABOVEUDL] else [Ca.RESULT] + [Mg] + [IN1])',
             'analyses': {'Ca': '<5', 'Mg': '5'},
             'interims': {'IN1': '10'},
             'exresult': '10.0'
             },

            {'formula': '[Comment] if [Comment] == "uncertain" else ([Ca] + [Mg])',
             'analyses': {'Ca': '5', 'Mg': '5'},
             'interims': {'Comment': 'uncertain'},
             'result_types': {'Comment': 'str'},
             'exresult': 'uncertain'
             },

            {'formula': '[Comment] if [Comment] == "uncertain" else ([Ca] + [Mg])',
             'analyses': {'Ca': '5', 'Mg': '5'},
             'interims': {'Comment': 'certain'},
             'result_types': {'Comment': 'str'},
             'exresult': '10.0'
             },

            {'formula': '[Comment] if [Comment] == "uncertain" else ([Ca] + [Mg])',
             'analyses': {'Ca': '5', 'Mg': '5'},
             'interims': {'Comment': '10'},
             'result_types': {'Comment': 'str'},
             'exresult': '10.0'
             },
        ]
        # New formulas for precision testing
        self.formulas_precision = [
            {'formula': '[Ca]/[Mg]',
             'analyses': {'Ca': '10', 'Mg': '15'},
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
             'test_uncertainties_precision': [
                 {'uncertainties': [
                    {
                         'intercept_min': 0,
                         'intercept_max': 10,
                         'errorvalue': 0.056
                    },
                 ],
                     'expected_result': '0.67'
                 },
                 {'uncertainties': [
                    {
                        'intercept_min': 0.002,
                        'intercept_max': 20,
                        'errorvalue': 0.1
                    }
                 ],
                     'expected_result': '0.7'
                 },
             ],
             },
            {'formula': '[Ca]/[Mg]*[IN1]',
             'analyses': {'Ca': '100', 'Mg': '20'},
             'interims': {'IN1': '0.12'},
             'test_fixed_precision': [
                 {
                     'fixed_precision': 5,
                     'expected_result': '0.60000',
                 },
                 {
                     'fixed_precision': 2,
                     'expected_result': '0.60'
                 },
                 {
                     'fixed_precision': 1,
                     'expected_result': '0.6'
                 },
                 {
                     'fixed_precision': 0,
                     'expected_result': '1'
                 },
                 {
                     'fixed_precision': -1,
                     'expected_result': '1'
                 },
                 {
                     'fixed_precision': -5,
                     'expected_result': '1'
                 },
             ],
             'test_uncertainties_precision': [
                 {'uncertainties': [
                     {
                         'intercept_min': 0,
                         'intercept_max': 10,
                         'errorvalue': 0.1
                     },
                     {
                         'intercept_min': 11,
                         'intercept_max': 20,
                         'errorvalue': 0.056
                     }
                 ],
                     'expected_result': '0.6'
                 },
                 {'uncertainties': [
                     {
                         'intercept_min': 0.1,
                         'intercept_max': 0.6,
                         'errorvalue': 0.1
                     },
                     {
                         'intercept_min': 0.66,
                         'intercept_max': 20,
                         'errorvalue': 0.056
                     }
                 ],
                     'expected_result': '0.6',
                 },
             ],
             },
            {'formula': '[Ca]/[Mg]',
             'analyses': {'Ca': '10', 'Mg': 1},
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
             'test_uncertainties_precision': [
                 {'uncertainties': [
                     {
                         'intercept_min': 0,
                         'intercept_max': 10,
                         'errorvalue': 0.1
                     },
                     {
                         'intercept_min': 11,
                         'intercept_max': 20,
                         'errorvalue': 0.056
                     }
                 ],
                     'expected_result': '10.0'
                 },
             ],
             },
            {'formula': '[Ca]/[Mg]',
             'analyses': {'Ca': '1', 'Mg': '20'},
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
             'test_uncertainties_precision': [
                 {'uncertainties': [
                     {
                         'intercept_min': 0,
                         'intercept_max': 0.01,
                         'errorvalue': 0.01
                     },
                     {
                         'intercept_min': 11,
                         'intercept_max': 20,
                         'errorvalue': 0.056
                     }
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
            result_types = f.get("result_types") or {}
            for k, v in f['interims'].items():
                result_type = result_types.get(k) or ""
                interims.append({'keyword': k, 'title': k, 'value': v,
                                 'hidden': False,
                                 'result_type': result_type,
                                 'choices': u'',
                                 'unit': ''})
            self.calculation.setInterimFields(interims)
            self.assertTrue(self.calculation.getInterimFields() == interims)

            # Test fixture
            # We need to take a new snapshot after the modifications
            modified(self.calculation)

            # Create the AR
            client = self.portal.clients['client-1']
            sampletype = self.portal.setup.sampletypes['sampletype-1']
            values = {'Client': client.UID(),
                      'Contact': client.getContacts()[0].UID(),
                      'DateSampled': '2015-01-01',
                      'SampleType': sampletype.UID()}
            request = {}
            services = [s.UID() for s in self.services] + \
                [self.calcservice.UID()]
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
                        self.assertEqual(an.getResult(), strres)
                    else:
                        self.assertEqual(an.getResult(), f['analyses'][key])
                elif key == self.calcservice.getKeyword():
                    calcanalysis = an

                # Set interims
                interims = an.getInterimFields()
                intermap = []
                for i in interims:
                    if i['keyword'] in f['interims']:
                        ival = f['interims'][i['keyword']]
                        result_type = i.get("result_type")
                        intermap.append({'keyword': i['keyword'],
                                        'value': ival,
                                         'title': i['title'],
                                         'hidden': i['hidden'],
                                         'result_type': result_type,
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

            result = calcanalysis.getResult()
            exresult = f['exresult']
            self.assertEqual(result, exresult)

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
            for k, v in f['interims'].items():
                interims.append({'keyword': k, 'title': k, 'value': v,
                                 'hidden': False, 'result_type': 'numeric',
                                 'choices': u'', 'unit': ''})
            self.calculation.setInterimFields(interims)
            self.assertEqual(self.calculation.getInterimFields(), interims)

            # Test fixture
            # We need to take a new snapshot after the modifications
            modified(self.calculation)

            for r in f['test_fixed_precision']:
                # Define precision
                services_obj = [s for s in self.services] + [self.calcservice]
                for service in services_obj:
                    service.setPrecision(r['fixed_precision'])
                # Create the AR
                client = self.portal.clients['client-1']
                sampletype = self.portal.setup.sampletypes['sampletype-1']
                values = {'Client': client.UID(),
                          'Contact': client.getContacts()[0].UID(),
                          'DateSampled': '2015-01-01',
                          'SampleType': sampletype.UID()}
                request = {}
                services = [s.UID() for s in self.services] + \
                    [self.calcservice.UID()]
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
                            self.assertEqual(
                                an.getResult(), str(float(strres)))
                        else:
                            # The analysis' results have to be always strings
                            self.assertEqual(
                                an.getResult(), str(f['analyses'][key]))
                    elif key == self.calcservice.getKeyword():
                        calcanalysis = an

                    # Set interims
                    interims = an.getInterimFields()
                    intermap = []
                    for i in interims:
                        if i['keyword'] in f['interims']:
                            ival = float(f['interims'][i['keyword']])
                            result_type = i.get(
                                'result_type', i.get('type', ''))
                            intermap.append({'keyword': i['keyword'],
                                             'value': ival,
                                             'title': i['title'],
                                             'hidden': i['hidden'],
                                             'result_type': result_type,
                                             'unit': i['unit']})
                        else:
                            intermap.append(i)
                    an.setInterimFields(intermap)
                    self.assertEqual(an.getInterimFields(), intermap)

                # Let's go.. calculate and check result
                calcanalysis.calculateResult(True, True)
                self.assertEqual(
                    calcanalysis.getFormattedResult(), r['expected_result'])

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
                                 'hidden': False, 'result_type': 'numeric',
                                 'choices': u'', 'unit': ''})
            self.calculation.setInterimFields(interims)
            self.assertEqual(self.calculation.getInterimFields(), interims)

            # Test fixture
            # We need to take a new snapshot after the modifications
            modified(self.calculation)

            for r in f['test_uncertainties_precision']:
                # Define precision
                services_obj = [s for s in self.services] + [self.calcservice]

                for service in services_obj:
                    service.setPrecisionFromUncertainty(True)
                    service.setUncertainties(r['uncertainties'])
                # Create the AR
                client = self.portal.clients['client-1']
                sampletype = self.portal.setup.sampletypes['sampletype-1']
                values = {'Client': client.UID(),
                          'Contact': client.getContacts()[0].UID(),
                          'DateSampled': '2015-01-01',
                          'SampleType': sampletype.UID()}
                request = {}
                services = [s.UID() for s in self.services] + \
                    [self.calcservice.UID()]
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
                            self.assertEqual(
                                an.getResult(), str(float(strres)))
                        else:
                            # The analysis' results have to be always strings
                            self.assertEqual(
                                an.getResult(), str(f['analyses'][key]))
                    elif key == self.calcservice.getKeyword():
                        calcanalysis = an

                    # Set interims
                    interims = an.getInterimFields()
                    intermap = []
                    for i in interims:
                        if i['keyword'] in f['interims']:
                            ival = float(f['interims'][i['keyword']])
                            result_type = i.get(
                                'result_type', i.get('type', ''))
                            intermap.append({'keyword': i['keyword'],
                                             'value': ival,
                                             'title': i['title'],
                                             'hidden': i['hidden'],
                                             'result_type': result_type,
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
                    r['expected_result'])


class TestCalculationFormula(unittest.TestCase):

    formula = "([PSD180Mass] / [PSDTotalmass]) * 100"
    parameters = {"PSD180Mass": "10", "PSDTotalmass": "20"}

    def test_empty_formula(self):
        for formula in ("", " \t\n", None):
            self.assertEqual(calculate_formula(formula), "")

    def test_integer_parameters_preserve_fraction(self):
        self.assertEqual(
            calculate_formula(self.formula, self.parameters), 50.0)

    def test_incomplete_test_values(self):
        for value in ("", " \t", None):
            self.assertEqual(calculate_formula(
                self.formula, {"PSD180Mass": value, "PSDTotalmass": "20"}),
                "Enter values for all test parameters.")

    def test_missing_test_parameter(self):
        self.assertEqual(calculate_formula(
            self.formula, {"PSDTotalmass": "20"}),
            "Enter values for all test parameters.")

    def test_zero_test_value(self):
        self.assertEqual(calculate_formula(
            self.formula, {"PSD180Mass": "0", "PSDTotalmass": "20"}), 0.0)

    def test_unused_blank_parameter(self):
        self.assertEqual(calculate_formula("10 / 20 * 100", {"unused": ""}), 50.0)

    def test_new_parameters_use_interim_defaults(self):
        form = {FIELD_FORMULA: self.formula}
        for index, (keyword, value) in enumerate(self.parameters.items()):
            prefix = "form.widgets.interim_fields.{}.widgets.".format(index)
            form[prefix + "keyword"] = keyword
            form[prefix + "value"] = value
        data = EditForm(None, None).update_test_parameters({"form": form})
        updates = {item["name"]: item["value"] for item in data["updates"]}
        self.assertEqual(updates[FIELD_TEST_VALUE.format(0)], "10")
        self.assertEqual(updates[FIELD_TEST_VALUE.format(1)], "20")
        self.assertEqual(updates[FIELD_TEST_RESULT], 50.0)

    def test_existing_test_value_overrides_interim_default(self):
        form = {
            FIELD_FORMULA: "[Mass] * 2",
            "form.widgets.interim_fields.0.widgets.keyword": "Mass",
            "form.widgets.interim_fields.0.widgets.value": "10",
            FIELD_TEST_KEYWORD.format(0): "Mass",
            FIELD_TEST_VALUE.format(0): "15",
        }
        data = EditForm(None, None).update_test_parameters({"form": form})
        updates = {item["name"]: item["value"] for item in data["updates"]}
        self.assertEqual(updates[FIELD_TEST_VALUE.format(0)], "15")
        self.assertEqual(updates[FIELD_TEST_RESULT], 30)

    def test_constant_division_preserves_fraction(self):
        self.assertEqual(calculate_formula("10 / 20 * 100"), 50.0)

    def test_explicit_floor_division(self):
        self.assertEqual(calculate_formula("10 // 20 * 100"), 0)

    def test_invalid_formula(self):
        self.assertTrue(calculate_formula("10 /").startswith("Syntax Error:"))

    def test_division_by_zero(self):
        self.assertTrue(calculate_formula("10 / 0").startswith("Division by 0:"))

    def test_live_preview(self):
        form = {FIELD_FORMULA: self.formula}
        for index, (keyword, value) in enumerate(self.parameters.items()):
            form[FIELD_TEST_KEYWORD.format(index)] = keyword
            form[FIELD_TEST_VALUE.format(index)] = value
        data = EditForm(None, None).update_test_parameters({"form": form})
        results = [item["value"] for item in data["updates"]
                   if item["name"] == FIELD_TEST_RESULT]
        self.assertEqual(results, [50.0])

    def test_empty_preview(self):
        data = EditForm(None, None).update_test_parameters(
            {"form": {FIELD_FORMULA: ""}})
        results = [item["value"] for item in data["updates"]
                   if item["name"] == FIELD_TEST_RESULT]
        self.assertEqual(results, [""])

    def test_stored_test_result(self):
        class TestCalculation(Calculation):
            # Resolve fields without requiring a portal_types tool.
            def accessor(self, name):
                return ICalculationSchema[name].get

            def mutator(self, name):
                return ICalculationSchema[name].set

        calculation = TestCalculation("test-calculation")
        calculation.formula = self.formula
        calculation.test_parameters = [
            {"keyword": keyword, "value": value}
            for keyword, value in self.parameters.items()]
        calculation.imports = []
        calculation.setTestResult("")
        self.assertEqual(calculation.getTestResult(), "50.0")



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCalculations))
    suite.addTest(unittest.makeSuite(TestCalculationFormula))
    return suite
