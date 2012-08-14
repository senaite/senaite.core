from Products.validation import validation
from Products.validation import validation as validationService
from bika.lims.testing import BIKA_LIMS_INTEGRATION_TESTING
from bika.lims.tests.base import BikaIntegrationTestCase
from plone.app.testing import *
from plone.testing import z2
import unittest

class Tests(BikaIntegrationTestCase):

    def test_UniqueFieldValidator(self):
        login(self.portal, TEST_USER_NAME)

        clients = self.portal.clients
        client1 = self.portal.clients['client-1']
        self.assertEqual(
            client1.schema.get('Name').validate('Norton Feeds', client1),
            u"Validation failed: 'Norton Feeds' is not unique")
        self.assertEqual(None,client1.schema.get('title').validate('Another Client', client1))

    def test_ServiceKeywordValidator(self):
        login(self.portal, TEST_USER_NAME)

        services = self.portal.bika_setup.bika_analysisservices
        service1 = services['analysisservice-1']

        self.assertEqual(
            service1.schema.get('Keyword').validate('', service1),
            u'Analysis Keyword is required, please correct.')
        self.assertEqual(
            service1.schema.get('Keyword').validate('&', service1),
            u'Validation failed: keyword contains invalid characters')
        self.assertEqual(
            service1.schema.get('Keyword').validate('Ash', service1),
            u"Validation failed: 'Ash': This keyword is already in use by service 'Ash'")
        self.assertEqual(
            service1.schema.get('Keyword').validate('TV', service1),
            u"Validation failed: 'TV': This keyword is already in use by calculation 'Titration'")
        self.assertEqual(None,service1.schema.get('Keyword').validate('VALID_KW', service1))

    def test_InterimFieldsValidator(self):
        login(self.portal, TEST_USER_NAME)

        calcs = self.portal.bika_setup.bika_calculations
        # Titration
        calc1 = calcs['calculation-1']

        interim_fields = []
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(None,calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST))

        interim_fields = [{'keyword': '&', 'title':'Titration Volume', 'unit':'','default':''},]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST),
            u"Validation failed: keyword contains invalid characters")

        interim_fields = [{'keyword': 'XXX', 'title':'Gross Mass', 'unit':'','default':''},
                          {'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST),
            u"Validation failed: column title 'Gross Mass' must have keyword 'GM'")

        interim_fields = [{'keyword': 'GM', 'title':'XXX', 'unit':'','default':''},
                          {'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST),
            u"Validation failed: keyword 'GM' must have column title 'Gross Mass'")

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST),
            u"Validation failed: 'TV': duplicate keyword")

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Volume', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST),
            u"Validation failed: 'Titration Volume': duplicate title")

        interim_fields = [{'keyword': 'Ash', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(
            calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST),
            u"Validation failed: 'Ash': This keyword is already in use by service 'Ash'")

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields
        self.portal.REQUEST['validated'] = None
        self.assertEqual(None,calc1.schema.get('InterimFields').validate(interim_fields, calc1, REQUEST=self.portal.REQUEST))

    def test_FormulaValidator(self):
        login(self.portal, TEST_USER_NAME)

        v = validationService.validatorFor('formulavalidator')
        calcs = self.portal.bika_setup.bika_calculations
        calc1 = calcs['calculation-1']

        interim_fields = [{'keyword': 'TV', 'title':'Titration Volume', 'unit':'','default':''},
                          {'keyword': 'TF', 'title':'Titration Factor', 'unit':'','default':''}]
        self.portal.REQUEST.form['InterimFields'] = interim_fields

        formula = "[TV] * [TF] * [Ash] * [Wrong]"
        self.failUnlessEqual(
            v(formula, instance=calc1, field=calc1.schema.get('Formula'), REQUEST=self.portal.REQUEST),
            "Validation failed: Keyword 'Wrong' is invalid")

        formula = "[TV] * [TF] * [Ash]"
        self.assertEqual(True,v(formula, instance=calc1, field=calc1.schema.get('Formula'), REQUEST=self.portal.REQUEST))

    def test_CoordinateValidator(self):
        login(self.portal, TEST_USER_NAME)

        sp = self.portal.bika_setup.bika_samplepoints['samplepoint-1']

        latitude = {'degrees':'!','minutes':'2','seconds':'3', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(True, u"Validation failed: degrees must be numeric" in val)

        latitude = {'degrees':'0','minutes':'!','seconds':'3', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(True, u"Validation failed: minutes must be numeric" in val)

        latitude = {'degrees':'0','minutes':'0','seconds':'!', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(True, u"Validation failed: seconds must be numeric" in val)

        latitude = {'degrees':'0','minutes':'60','seconds':'0', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(True, u"Validation failed: minutes must be 0 - 59" in val)

        latitude = {'degrees':'0','minutes':'0','seconds':'60', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(True, u"Validation failed: seconds must be 0 - 59" in val)

        # latitude specific

        latitude = {'degrees':'91','minutes':'0','seconds':'0', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(True, u"Validation failed: degrees must be 0 - 90" in val)

        latitude = {'degrees':'90','minutes':'1','seconds':'0', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(True, u"Validation failed: degrees is 90; minutes must be zero" in val)

        latitude = {'degrees':'90','minutes':'0','seconds':'1', 'bearing':'N'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(True, u"Validation failed: degrees is 90; seconds must be zero" in val)

        latitude = {'degrees':'90','minutes':'0','seconds':'0', 'bearing':'E'}
        self.portal.REQUEST.form['Latitude'] = latitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Latitude').validate(latitude, sp)
        self.assertEqual(True, u"Validation failed: Bearing must be N/S" in val)

        # longitude specific

        longitude = {'degrees':'181','minutes':'0','seconds':'0', 'bearing':'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Longitude').validate(longitude, sp)
        self.assertEqual(True, u"Validation failed: degrees must be 0 - 180" in val)

        longitude = {'degrees':'180','minutes':'1','seconds':'0', 'bearing':'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Longitude').validate(longitude, sp)
        self.assertEqual(True, u"Validation failed: degrees is 180; minutes must be zero" in val)

        longitude = {'degrees':'180','minutes':'0','seconds':'1', 'bearing':'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Longitude').validate(longitude, sp)
        self.assertEqual(True, u"Validation failed: degrees is 180; seconds must be zero" in val)

        longitude = {'degrees':'0','minutes':'0','seconds':'0', 'bearing':'N'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        val = sp.schema.get('Longitude').validate(longitude, sp)
        self.assertEqual(True, u"Validation failed: Bearing must be E/W" in val)

        longitude = {'degrees':'1','minutes':'1','seconds':'1', 'bearing':'E'}
        self.portal.REQUEST.form['Longitude'] = longitude
        self.portal.REQUEST['validated'] = None
        self.assertEqual(None,sp.schema.get('Longitude').validate(longitude, sp))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_LIMS_INTEGRATION_TESTING
    return suite
