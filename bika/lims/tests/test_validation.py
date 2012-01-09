from Products.validation import validation
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from plone.app.testing import *
from plone.testing import z2

import unittest

class Tests(unittest.TestCase):

    layer = BIKA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

    def test_UniqueFieldValidator(self):
        login(self.portal, TEST_USER_NAME)

        clients = self.portal.clients
        clients.invokeFactory('Client', 'happy-hills-feeds')
        clients.client_2.processForm()
        self.assertEqual(clients.client_2.schema.get('title').validate('Client', clients.client_2),
                         "Validation failed: 'happy-hills-feeds' is in use.")
        self.assertEqual(None, clients.client_2.schema.get('title').validate('Another Client', clients.client_2))

    def test_ServiceKeywordValidator(self):
        login(self.portal, TEST_USER_NAME)

        services = self.portal.bika_setup.bika_analysisservices
        services.invokeFactory('AnalysisService', 'service_2')
        services.service_2.processForm()

        self.assertEqual(services.service_2.schema.get('Keyword').validate('Ash', services.service_2),
                         "Validation failed: 'Ash': This keyword is used by service 'Ash'.")
        self.assertEqual(services.service_2.schema.get('Keyword').validate('TV', services.service_2),
                         "Validation failed: 'TV': This keyword is used by calculation 'Titration'.")
        self.assertEqual(None, services.service_2.schema.get('Keyword').validate('ValidKeyword', services.service_2))

    def test_InterimFieldsValidator(self):
        login(self.portal, TEST_USER_NAME)

        calcs = self.portal.bika_setup.bika_calculations

        interim_fields = [{'keyword': 'T V', 'title':'Titration Volume', 'unit':'','default':''},]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.assertEqual(calcs.titration.schema.get('InterimFields').validate(interim_fields, calcs.titration, REQUEST=self.portal.REQUEST),
                         "Validation failed: keyword contains invalid characters.")

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TV', 'title':'Titration Volume 2', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.assertEqual(calcs.titration.schema.get('InterimFields').validate(interim_fields, calcs.titration, REQUEST=self.portal.REQUEST),
                         "Validation failed: 'TV': duplicate keyword.")

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Volume', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.assertEqual(calcs.titration.schema.get('InterimFields').validate(interim_fields, calcs.titration, REQUEST=self.portal.REQUEST),
                         "Validation failed: 'Titration Volume': duplicate title.")

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''},
                          {'keyword': 'Ash', 'title':'Temp', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.assertEqual(calcs.titration.schema.get('InterimFields').validate(interim_fields, calcs.titration, REQUEST=self.portal.REQUEST),
                         "Validation failed: 'Ash': This keyword is used by service 'Ash'.")

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.assertEqual(None, calcs.titration.schema.get('InterimFields').validate(interim_fields, calcs.titration, REQUEST=self.portal.REQUEST))

    def test_FormulaValidator(self):
        login(self.portal, TEST_USER_NAME)

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]

        calcs = self.portal.bika_setup.bika_calculations
        calcs.invokeFactory('Calculation', 'calc_1', title='Titration', InterimFields=interim_fields)
        calcs.calc_1.processForm()

        formula = "%(TV)f * %(TF)f * %(Ash)f * %(Wrong)f"
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST.form['Formula'] = formula
        self.assertEqual(calcs.titration.schema.get('Formula').validate(formula, calcs.titration, REQUEST=self.portal.REQUEST),
                         "Validation failed: Keyword 'Wrong' is invalid.")

        formula = "%(TV)f * %(TF)f * %(Ash)f"
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST.form['Formula'] = formula
        self.assertEqual(None, calcs.titration.schema.get('Formula').validate(formula, calcs.titration, REQUEST=self.portal.REQUEST))

        formula = "[TV] * [TF] * [Ash]"
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST.form['Formula'] = formula
        self.assertEqual(None, calcs.titration.schema.get('Formula').validate(formula, calcs.titration, REQUEST=self.portal.REQUEST))

    def test_CoordinateValidator(self):
        login(self.portal, TEST_USER_NAME)

        sp = self.portal.bika_setup.bika_samplepoints['samplepoint-1']
        field = sp.schema.get('Latitude')

        import pdb;pdb.set_trace()

        field.validate({'degrees':'1','minutes':'2','seconds':'3', 'bearing':'n'},
                       sp, {}, {'REQUEST':self.portal.REQUEST})

        self.assertEqual(sp.schema.get('Latitude').validate('59x25x25xE', sp),
                         "Invalid Latitude. Use DEG MIN SEC N/S")
        self.assertEqual(True, sp.schema.get('Latitude').validate('59degrees 25mins 25N', sp))
        self.assertEqual(sp.schema.get('Longitude').validate('asdf', sp),
                         "Invalid Latitude. Use DEG MIN SEC E/W")
        self.assertEqual(sp.schema.get('Longitude').validate('59 25 25 N', sp),
                         "Invalid Latitude. Use DEG MIN SEC E/W")
        self.assertEqual(True, sp.schema.get('Longitude').validate('59degrees 25mins 25E', sp))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
