from bika.lims import logger
from bika.lims.content.analysis import Analysis
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils.analysisrequest import create_analysisrequest
from bika.lims.workflow import doActionFor
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
import unittest

try:
    import unittest2 as unittest
except ImportError: # Python 2.7
    import unittest


class TestCalculations(BikaFunctionalTestCase):
    layer = BIKA_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestCalculations, self).setUp()
        login(self.portal, TEST_USER_NAME)

        # Calculation: Total Hardness
        # Initial formula: [Ca] + [Mg]
        calcs = self.portal.bika_setup.bika_calculations
        self.calculation = [calcs[k] for k in calcs if calcs[k].title=='Total Hardness'][0]

        # Service with calculation: Tot. Harndess (THCaCO3)
        servs = self.portal.bika_setup.bika_analysisservices
        self.calcservice = [servs[k] for k in servs if servs[k].title=='Tot. Hardness (THCaCO3)'][0]
        self.calcservice.setUseDefaultCalculation(False)
        self.calcservice.setDeferredCalculation(self.calculation)
        self.calcservice.setLowerDetectionLimit('10')
        self.calcservice.setUpperDetectionLimit('20')
        self.calcservice.setAllowManualDetectionLimit(True)

        # Analysis Services: Ca and Mg
        self.services = self.calculation.getDependentServices()

        # Formulas to test
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

    def tearDown(self):
        # Service with calculation: Tot. Harndess (THCaCO3)
        self.calculation.setFormula('[Ca] + [Mg]')
        self.calcservice.setUseDefaultCalculation(True)
        self.calcservice.setLowerDetectionLimit('0')
        self.calcservice.setUpperDetectionLimit('10000')
        self.calcservice.setAllowManualDetectionLimit(False)
        super(TestCalculations, self).tearDown()

    def test_ar_calculations(self):
        # Input results
        # Client:       Happy Hills
        # SampleType:   Apple Pulp
        # Contact:      Rita Mohale
        # Analyses:     [Calcium, Mg, Total Hardness]
        for f in self.formulas:
            # Set custom calculation
            self.calculation.setFormula(f['formula'])
            self.assertEqual(self.calculation.getFormula(), f['formula'])
            interims = []
            for k,v in f['interims']:
                interims.append({'keyword': k, 'title':k, 'value': v,
                                 'hidden': False, 'type': 'int',
                                 'unit': ''});
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

            # Set results and interims
            calcanalysis = None
            for an in ar.getAnalyses():
                an = an.getObject()
                key = an.getKeyword()
                if key in f['analyses']:
                    an.setResult(f['analyses'][key])
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

            # Let's go.. check result
            calcanalysis.calculateResult(True, True)
            self.assertEqual(calcanalysis.getResult(), f['exresult'])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCalculations))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
