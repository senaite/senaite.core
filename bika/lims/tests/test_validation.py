from Products.validation import validation
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from plone.app.testing import SITE_OWNER_NAME, TEST_USER_NAME, login, setRoles
from plone.testing import z2

import unittest

class TestValidation(unittest.TestCase):

    layer = BIKA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

    def test_UniqueFieldValidator(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

        clients = self.portal.clients
        clients.invokeFactory('Client', 'client_1', Name='A Client')
        clients.client_1.processForm()
        clients.invokeFactory('Client', 'client_2')
        clients.client_2.processForm()
        self.assertEqual(clients.client_2.schema.get('title').validate('A Client', clients.client_2),
                         "Validation failed: 'A Client' is in use.")
        self.assertEqual(None, clients.client_2.schema.get('title').validate('Another Client', clients.client_2))

        calcs = self.portal.bika_setup.bika_calculations
        calcs.invokeFactory('Calculation', 'calc_1', title='A Calc')
        calcs.calc_1.processForm()
        calcs.invokeFactory('Calculation', 'calc_2')
        calcs.calc_2.processForm()
        self.assertEqual(calcs.calc_2.schema.get('title').validate('A Calc', calcs.calc_2),
                         "Validation failed: 'A Calc' is in use.")
        self.assertEqual(None, calcs.calc_2.schema.get('title').validate('Another Calc', calcs.calc_2))

    def test_ServiceKeywordValidator(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

        calcs = self.portal.bika_setup.bika_calculations
        calcs.invokeFactory('Calculation', 'calc_1', title='Titration',
                            InterimFields=[{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                                           {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}])
        calcs.calc_1.processForm()

        services = self.portal.bika_setup.bika_analysisservices
        services.invokeFactory('AnalysisService', 'service_1', title='Temperature', Keyword='Temp')
        services.service_1.processForm()
        services.invokeFactory('AnalysisService', 'service_2')
        services.service_2.processForm()
        self.assertEqual(services.service_2.schema.get('Keyword').validate('Temp', services.service_2),
                         "Validation failed: 'Temp': This keyword is used by service 'Temperature'.")
        self.assertEqual(services.service_2.schema.get('Keyword').validate('TV', services.service_2),
                         "Validation failed: 'TV': This keyword is used by calculation 'Titration'.")
        self.assertEqual(None, services.service_2.schema.get('Keyword').validate('OtherTemp', services.service_2))

    def test_InterimFieldsValidator(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

        calcs = self.portal.bika_setup.bika_calculations
        calcs.invokeFactory('Calculation', 'calc_1', title='Titration',
                            InterimFields=[{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                                           {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}])
        calcs.calc_1.processForm()

        services = self.portal.bika_setup.bika_analysisservices
        services.invokeFactory('AnalysisService', 'service_1', title='Temperature', Keyword='Temp')
        services.service_1.processForm()

        interim_fields = [{'keyword': 'T V', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.assertEqual(calcs.calc_1.schema.get('InterimFields').validate(interim_fields, calcs.calc_1, REQUEST=self.portal.REQUEST),
                         "Validation failed(isValidKeyword): 'T V' Keyword contains invalid characters.")

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TV', 'title':'Titration Volume 2', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.assertEqual(calcs.calc_1.schema.get('InterimFields').validate(interim_fields, calcs.calc_1, REQUEST=self.portal.REQUEST),
                         "Validation failed: 'TV': duplicate keyword.")

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Volume', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.assertEqual(calcs.calc_1.schema.get('InterimFields').validate(interim_fields, calcs.calc_1, REQUEST=self.portal.REQUEST),
                         "Validation failed: 'Titration Volume': duplicate title.")

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''},
                          {'keyword': 'Temp', 'title':'Temp', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.assertEqual(calcs.calc_1.schema.get('InterimFields').validate(interim_fields, calcs.calc_1, REQUEST=self.portal.REQUEST),
                         "Validation failed: 'Temp': This keyword is used by service 'Temperature'.")

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.assertEqual(None, calcs.calc_1.schema.get('InterimFields').validate(interim_fields, calcs.calc_1, REQUEST=self.portal.REQUEST))

    def test_FormulaValidator(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]

        calcs = self.portal.bika_setup.bika_calculations
        calcs.invokeFactory('Calculation', 'calc_1', title='Titration', InterimFields=interim_fields)
        calcs.calc_1.processForm()

        services = self.portal.bika_setup.bika_analysisservices
        services.invokeFactory('AnalysisService', 'service_1', title='Temperature', Keyword='Temp')
        services.service_1.processForm()

        formula = "%(TV)f * %(TF)f * %(Temp)f * %(Wrong)f"
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST.form['Formula'] = formula
        self.assertEqual(calcs.calc_1.schema.get('Formula').validate(formula, calcs.calc_1, REQUEST=self.portal.REQUEST),
                         "Validation failed: Keyword 'Wrong' does not exist.")

        formula = "%(TV)f * %(TF)f * %(Temp)f"
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST.form['Formula'] = formula
        self.assertEqual(None, calcs.calc_1.schema.get('Formula').validate(formula, calcs.calc_1, REQUEST=self.portal.REQUEST))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestValidation))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
