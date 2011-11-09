from Products.validation import validation
from bika.lims.testing import BIKA_INTEGRATION_TESTING
from plone.app.testing import SITE_OWNER_NAME, TEST_USER_NAME, login, setRoles
from plone.testing import z2

import unittest

class Tests(unittest.TestCase):

    layer = BIKA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

    def test_UniqueFieldValidator(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

        clients = self.portal.clients
        clients.invokeFactory('Client', 'client_2')
        clients.client_2.processForm()
        self.assertEqual(clients.client_2.schema.get('title').validate('Client', clients.client_2),
                         "Validation failed: 'Client' is in use.")
        self.assertEqual(None, clients.client_2.schema.get('title').validate('Another Client', clients.client_2))

    def test_ServiceKeywordValidator(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

        services = self.portal.bika_setup.bika_analysisservices
        services.invokeFactory('AnalysisService', 'service_2')
        services.service_2.processForm()

        self.assertEqual(services.service_2.schema.get('Keyword').validate('Ash', services.service_2),
                         "Validation failed: 'Ash': This keyword is used by service 'Ash'.")
        self.assertEqual(services.service_2.schema.get('Keyword').validate('TV', services.service_2),
                         "Validation failed: 'TV': This keyword is used by calculation 'Titration'.")
        self.assertEqual(None, services.service_2.schema.get('Keyword').validate('ValidKeyword', services.service_2))

    def test_InterimFieldsValidator(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

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
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

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
        # AVS 
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

        folder = self.portal.bika_setup.bika_samplepoints
        folder.invokeFactory('SamplePoint', 'sp_1')
        folder.sp_1.edit(Latitude = '52 12 17.0 N',
                         Longitude = '000 08 26.0 E')
        folder.sp_1.processForm()
        sp_1 = folder.sp_1

##        import pdb;pdb.set_trace()
        self.assertEqual(sp_1.schema.get('Latitude').validate('asdf', sp_1),
                         "Invalid Latitude. Use DEG MIN SEC N/S")
        self.assertEqual(sp_1.schema.get('Latitude').validate('59x25x25xE', sp_1),
                         "Invalid Latitude. Use DEG MIN SEC N/S")
        self.assertEqual(True, sp_1.schema.get('Latitude').validate('59degrees 25mins 25N', sp_1))
        self.assertEqual(sp_1.schema.get('Longitude').validate('asdf', sp_1),
                         "Invalid Latitude. Use DEG MIN SEC E/W")
        self.assertEqual(sp_1.schema.get('Longitude').validate('59 25 25 N', sp_1),
                         "Invalid Latitude. Use DEG MIN SEC E/W")
        self.assertEqual(True, sp_1.schema.get('Longitude').validate('59degrees 25mins 25E', sp_1))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_INTEGRATION_TESTING
    return suite
